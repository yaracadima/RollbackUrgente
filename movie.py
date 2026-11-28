class Movie:
    def __init__(
        self, title, genre, year, poster_url, synopsis, director, duration, showtimes
    ):
        self.title = title
        self.genre = genre
        self.year = year
        self.poster_url = poster_url
        self.synopsis = synopsis
        self.director = director
        self.duration = duration
        self.showtimes = showtimes

    def to_document(self):
        return {
            "title": self.title,
            "genre": self.genre,
            "year": self.year,
            "poster_url": self.poster_url,
            "synopsis": self.synopsis,
            "director": self.director,
            "duration": self.duration,
            "showtimes": self.showtimes,
        }
