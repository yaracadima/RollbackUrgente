from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from flask import Flask, render_template, request, redirect, url_for, abort
from bson.objectid import ObjectId
from bson.errors import InvalidId
from PIL import Image, ImageOps
from werkzeug.utils import secure_filename

import database as dbase
from filters import build_query, clean_term
from movie import Movie
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

db = dbase.dbConnection()
movies_collection = db["movies"]

# Validar ID de MongoDB
def get_movie(id):
    try:
        movie = movies_collection.find_one({
            "_id": ObjectId(id)
        })
        if movie is None:
            abort(404, description="Película no encontrada.")
        return movie
    except InvalidId:
        abort(404, description="Película no encontrada.")

@app.route("/")
def catalog_home():
    return render_template("home.html")

def save_poster(poster, title):
    try:
        with Image.open(poster.stream) as image:
            if image.format not in {"JPEG", "PNG", "WEBP"}:
                abort(400, description="El póster debe ser JPG, PNG o WebP.")
            if image.width * image.height > 20_000_000:
                abort(400, description="La resolución del póster es demasiado grande.")
            image.thumbnail((1800, 1800))
            poster_image = ImageOps.exif_transpose(image).convert("RGB")
    except (OSError, Image.DecompressionBombError):
        abort(400, description="Selecciona un archivo de imagen válido para el póster.")

    title_slug = secure_filename(title).lower().replace("_", "-")[:70] or "pelicula"
    filename = f"{title_slug}-{uuid4().hex}.jpg"
    poster_dir = Path(app.static_folder) / "posters"
    poster_dir.mkdir(parents=True, exist_ok=True)
    poster_image.save(poster_dir / filename, format="JPEG")
    return url_for("static", filename=f"posters/{filename}")


# HU-01: Registrar película
@app.route("/movies/new", methods=["GET", "POST"])
def new_movie():
    if request.method == "GET":
        return render_template("movies/create.html")

    title = request.form.get("title", "").strip()
    genre = request.form.get("genre", "").strip()
    poster_url = request.form.get("poster_url", "").strip()
    synopsis = request.form.get("synopsis", "").strip()
    director = request.form.get("director", "").strip()
    duration_text = request.form.get("duration", "").strip()

    if not title or not genre:
        abort(400, description="El título y el género son obligatorios.")

    try:
        year = int(request.form.get("year", ""))
    except ValueError:
        abort(400, description="El año debe ser un número entero.")
    try:
        duration = int(duration_text) if duration_text else None
        if duration is not None and duration < 1:
            raise ValueError
    except ValueError:
        abort(400, description="La duración debe ser un número entero mayor que cero.")

    showtimes = []
    bolivia = timezone(timedelta(hours=-4))
    for starts_at_text in request.form.getlist("starts_at"):
        starts_at_text = starts_at_text.strip()
        if not starts_at_text:
            continue
        try:
            local_start = datetime.strptime(starts_at_text, "%Y-%m-%dT%H:%M")
        except ValueError:
            abort(400, description="Selecciona una fecha y hora válidas.")

        if local_start.year < year:
            abort(400, description=f"La función debe programarse en {year} o después.")

        showtimes.append(
            local_start.replace(tzinfo=bolivia).astimezone(timezone.utc)
        )

    poster = request.files.get("poster")
    if poster:
        poster_url = save_poster(poster, title)

    movie = Movie(
        title=title,
        genre=genre,
        year=year,
        poster_url=poster_url,
        synopsis=synopsis,
        director=director,
        duration=duration,
        showtimes=showtimes,
    )
    movies_collection.insert_one(movie.to_document())
    return redirect(url_for("list_movies"))

#HU-02: Consultar ficha de una pelicula
@app.route("/movies/<movie_id>")
def movie_detail(movie_id):
    movie = get_movie(movie_id)

    # Convertir la hora actual a la zona horaria de Bolivia
    bolivia = timezone(timedelta(hours=-4))
    now_utc = datetime.now(timezone.utc)
    upcoming = []

    for starts_at in movie.get("showtimes", []):
        if starts_at.tzinfo is None:
            starts_at = starts_at.replace(tzinfo=timezone.utc)


        if starts_at >= now_utc:
            upcoming.append(starts_at.astimezone(bolivia))
    upcoming.sort()
    return render_template("movies/detail.html", movie=movie, upcoming=upcoming)


# HU-03: Editar los datos de la película
@app.route("/movies/<movie_id>/edit", methods=["GET", "POST"])
def update_movie(movie_id):
    movie = get_movie(movie_id)
    if request.method == "GET":
        return render_template("movies/edit.html", movie=movie)

    title = request.form.get("title", "").strip()
    genre = request.form.get("genre", "").strip()
    if not title or not genre:
        abort(400, description="El título y el género son obligatorios.")

    try:
        year = int(request.form.get("year", ""))
        if not 1 <= year <= 9999:
            raise ValueError
    except ValueError:
        abort(400, description="El año de estreno debe ser válido.")

    duration_text = request.form.get("duration", "").strip()
    try:
        duration = int(duration_text) if duration_text else None
        if duration is not None and duration < 1:
            raise ValueError
    except ValueError:
        abort(400, description="La duración debe ser un número entero mayor que cero.")

    bolivia = timezone(timedelta(hours=-4))
    for showtime in movie.get("showtimes", []):
        starts_at = showtime.get("starts_at") if isinstance(showtime, dict) else showtime
        if isinstance(starts_at, datetime):
            if starts_at.tzinfo is None:
                starts_at = starts_at.replace(tzinfo=timezone.utc)
            if starts_at.astimezone(bolivia).year < year:
                abort(400, description="El año de estreno no puede ser posterior a una función registrada.")

    fields = {
        "title": title,
        "genre": genre,
        "year": year,
        "synopsis": request.form.get("synopsis", "").strip(),
        "director": request.form.get("director", "").strip(),
        "duration": duration,
    }
    poster = request.files.get("poster")
    if poster:
        fields["poster_url"] = save_poster(poster, title)

    result = movies_collection.update_one({"_id": movie["_id"]}, {"$set": fields})
    if result.matched_count == 0:
        abort(404, description="Película no encontrada.")

    return redirect(url_for("list_movies"))

# HU-05: listar el catálogo de películas
@app.route("/movies")
def list_movies():
    q = clean_term(request.args.get("q"))
    movies = list(
        movies_collection.find(build_query(q)).sort([("title", 1), ("year", -1)])
    )
    return render_template("movies/index.html", movies=movies, q=q)

if __name__ == "__main__":
    app.run(debug=True, port=4000)
