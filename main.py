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
    try:
        storage = StorageCsv(csv_file_path)
    except Exception as e:
        print(f"Error initializing storage: {e}")
        return  # Exit if storage initialization fails

    # Create the MovieApp instance, passing the storage and template folder path
    try:
        movie_app = MovieApp(storage, template_folder=templates_dir_path)
    except Exception as e:
        print(f"Error initializing MovieApp: {e}")
        return  # Exit if MovieApp initialization fails

    # Run the application
    movie_app.run()

if __name__ == "__main__":
    main()