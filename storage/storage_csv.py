# storage_csv.py
import csv

class StorageCsv:
    """
    A class to handle movie storage in a CSV file.
    Implements the IStorage interface.
    """
    def __init__(self, filename):
        """
        Initializes the storage with a filename.
        """
        self._filename = filename
        self.movies = self._load_movies()

    def _load_movies(self):
        """
        Loads movies from the CSV file.  Returns an empty dictionary if the file doesn't exist or is empty.
        """
        movies = {}
        try:
            with open(self._filename, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                # Check for empty file *before* attempting to read
                try:
                    for row in reader:
                        title = row.get('title')  # Safely get title and use get method
                        rating_str = row.get('rating')  # Safely get rating as string
                        year_str = row.get('year')  # Safely get year as string
                        poster = row.get('poster')  # Safely get poster as string

                        if not title:
                            print("Warning: Skipping row with missing title.")
                            continue  # Skip if title is missing

                        try:
                            rating = float(
                                rating_str) if rating_str else 0.0  # Default rating of 0.0 if missing or None
                            year = int(year_str) if year_str else 1900  # Default year, to prevent crash
                        except ValueError:
                            print(f"Warning: Invalid data in row. Skipping: {row}")
                            continue

                        movies[title] = {
                            "title": title,
                            "rating": rating,
                            "year": year,
                            "poster": poster
                        }
                except StopIteration: # handle empty file with headers.
                   print(f"Warning: CSV file is empty: {self._filename}")

        except FileNotFoundError:
            print(f"Warning: CSV file not found: {self._filename}. Starting with empty movie list.")
            # Create the file on first load.
            self._save_movies() # Creates an empty file with headers
        except (csv.Error, ValueError) as e:
            print(f"Error loading CSV file: {e}")

        return movies


    def _save_movies(self):
        """
        Saves movies to the CSV file.
        """
        try:
            with open(self._filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['title', 'rating', 'year', 'poster']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()  # Write the header row
                for movie_data in self.movies.values():
                    writer.writerow(movie_data)
        except Exception as e:
            print(f"Error saving CSV file: {e}")

    def list_movies(self):
        """
        Returns a dictionary of dictionaries
        that contains the movies information in the database.
        """
        return self.movies

    def add_movie(self, movie_data):
        """Adds a new movie."""
        title = movie_data.get('title')
        if not title:
            print("Error: Movie must have a title")
            return

        if title in self.movies:
            print(f"Error: Movie with title '{title}' already exists.")
            return

        self.movies[title] = movie_data
        self._save_movies()

    def delete_movie(self, movie_title):
        """Deletes a movie."""
        if movie_title in self.movies:
            del self.movies[movie_title]
            self._save_movies()
        else:
            print("Error: Movie does not exist.\n")

    def update_movie(self, movie_title, movie_data):
        """Updates a movie."""
        if movie_title in self.movies:
            self.movies[movie_title].update(movie_data)
            self._save_movies()
        else:
            print("Error: Movie does not exist.\n")

    def get_movie(self, movie_title):
        """Gets a movie by title."""
        return self.movies.get(movie_title)

    def movie_stats(self):
        """Calculates and returns movie statistics."""
        ratings = []
        for movie in self.movies.values():
            try:
                rating = float(movie.get('rating', 0.0))
                ratings.append(rating)
            except ValueError:
                print(f"Warning: Invalid rating '{movie.get('rating', 0)}' found for movie '{movie.get('title', 'Unknown')}'")

        if not ratings:
            return {"Average Rating": "No ratings available"}

        average_rating = sum(ratings) / len(ratings)
        return {"Average Rating": average_rating}