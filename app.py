"""Flask entry point for the CinePlus movie catalog."""

from flask import Flask, render_template

import database


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("home.html")

    @app.get("/movies")
    def list_movies():
        movies = list(
            database.get_movies_collection()
            .find()
            .sort([("title", 1), ("year", -1)])
        )
        return render_template("movies/index.html", movies=movies)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
