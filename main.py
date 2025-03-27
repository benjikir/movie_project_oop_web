# main.py

from storage.storage_csv import StorageCsv
from movie_app import MovieApp


def main():
    """
    Main function to create and run the MovieApp.
    """
    #relative path to the storage folder
    storage = StorageCsv('storage/movies.csv') #Correct path
    movie_app = MovieApp(storage)
    movie_app.run()

if __name__ == "__main__":
    main()