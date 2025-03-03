# main.py

from storage.storage_csv import StorageCsv
from movie_app import MovieApp


def main():
    """
    Main function to create and run the MovieApp.
    """

    storage = StorageCsv('storage/movies.csv')
    movie_app = MovieApp(storage)
    movie_app.run()

if __name__ == "__main__":
    main()