# storage_json.py
import json

class StorageJson:
    """
    A class to handle movie storage in a JSON file.
    """
    def __init__(self, filename):
        """
        Initializes the storage with a filename.
        """
        self._filename = filename
        self.movies = self._load_movies()

    def _load_movies(self):
        """Loads movies from the JSON file."""
        try:
            with open(self._filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print("Error decoding JSON file.  Using empty movie list.")
            return {}

    def _save_movies(self):
        """Saves movies to the JSON file."""
        try:
            with open(self._filename, 'w') as f:
                json.dump(self.movies, f, indent=4) #indent for readability
        except Exception as e:
            print(f"Error saving to JSON file: {e}")

    def list_movies(self):
        """Lists all movies."""
        return self.movies

    def add_movie(self, movie_data):
        """Adds a new movie."""
        new_id = str(len(self.movies) + 1) # Simple ID generation
        self.movies[new_id] = movie_data
        self._save_movies()

    def delete_movie(self, movie_id):
        """Deletes a movie."""
        if movie_id in self.movies:
            del self.movies[movie_id]
            self._save_movies()
        else:
            raise ValueError("Movie ID not found")

    def update_movie(self, movie_id, movie_data):
        """Updates a movie."""
        if movie_id in self.movies:
            self.movies[movie_id].update(movie_data)
            self._save_movies()
        else:
            raise ValueError("Movie ID not found")

    def get_movie(self, movie_id):
        """Gets a movie by ID."""
        return self.movies.get(movie_id)

    def movie_stats(self):
       """Calculates and returns movie statistics."""
       ratings = []
       for movie in self.movies.values():
           try:
               rating = float(movie.get('rating', 0))  # Handle missing ratings gracefully, convert to float
               ratings.append(rating)
           except ValueError:
               print(f"Warning: Invalid rating '{movie.get('rating', 0)}' found for movie '{movie.get('title', 'Unknown')}'")


       if not ratings:
           return {"Average Rating": "No ratings available"}

       average_rating = sum(ratings) / len(ratings)
       return {"Average Rating": average_rating}