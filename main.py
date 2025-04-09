# main.py

import os
from storage.storage_csv import StorageCsv
from movie_app import MovieApp

def main():
    """
    Main function to create and run the MovieApp.
    """
    # Define the path to the CSV file relative to this main.py script
    # Assuming 'storage' is a subfolder in the same directory as main.py
    csv_file_path = os.path.join('storage', 'movies.csv')

    # Define the path to the templates folder relative to this main.py script
    # Assuming 'templates' is a subfolder in the same directory as main.py
    templates_dir_path = 'templates' # Jinja2 loader needs the directory path

    # Create the storage instance
    storage = StorageCsv(csv_file_path)

    # Create the MovieApp instance, passing the storage and template folder path
    movie_app = MovieApp(storage, template_folder=templates_dir_path)

    # Run the application
    movie_app.run()

if __name__ == "__main__":
    main()