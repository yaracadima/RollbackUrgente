
from flask import Flask, render_template, request, redirect, url_for, abort
from bson.objectid import ObjectId
from bson.errors import InvalidId

import database as dbase
from filters import build_query, clean_term

app = Flask(__name__)

db = dbase.dbConnection()
movies_collection = db["movies"]


@app.route("/")
def catalog_home():
    return render_template("home.html")

#H01- Registrar pelicula
@app.route("/movies/new", methods=["GET", "POST"])
def new_movie():
    if request.method == "GET":
        return render_template("movies/create.html")

    title = request.form.get("title", "").strip()
    genre = request.form.get("genre", "").strip()
    poster_url = request.form.get("poster_url", "").strip()

    if not title or not genre:
        abort(400, description="El título y el género son obligatorios.")

    try:
        year = int(request.form.get("year", ""))
    except ValueError:
        abort(400, description="El año debe ser un número entero.")

    movie = {
        "title": title,
        "genre": genre,
        "year": year,
        "poster_url": poster_url,
    }

    movies_collection.insert_one(movie)
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
