# movie_app.py
import os
import requests  # Import the requests library
import random



class MovieApp:
    def __init__(self, storage):
        """
        Initializes the MovieApp with a storage object.
        """
        self._storage = storage
        self.movies = self._storage.list_movies()  # Load movies on initialization
        self._running = True
        # OMDB_API_KEY="4d55412d" #include the api_key not in env extern include it here
        self.omdb_api_key = os.environ.get("OMDB_API_KEY") or "4d55412d"  # Get API key from environment variable or use hardcoded value as fallback
        if not self.omdb_api_key:
            print("Error: OMDB_API_KEY not found in environment variables.")

    def _print_menu(self):
        """Prints the available menu options."""
        print("********** My Movies Database **********\n")
        print("Menu:")
        menu_options = [
            "Exit",
            "List Movies",
            "Add Movie",
            "Delete Movie",
            "Update Movie",
            "Stats",
            "Random movie",
            "Search movie",
            "Movies sorted by rating",
            "Generate website",
        ]
        for index, option in enumerate(menu_options):
            print(f"{index}. {option}")
        print("-" * 20)

    def _get_movie_from_omdb(self, title):
        """Fetches movie data from OMDb API."""
        if not self.omdb_api_key:
            print("OMDB_API_KEY is not set. Cannot fetch movie data.")
            return None

        try:
            url = f"http://www.omdbapi.com/?t={title}&apikey={self.omdb_api_key}"
            print(f"API URL: {url}")  # Debugging: Print the API URL

            response = requests.get(url, timeout=5)
            response.raise_for_status()  # Raise HTTPError for bad responses

            print(f"Response status code: {response.status_code}")  # Debugging: Print Status Code
            data = response.json()

            print(f"Raw JSON response: {data}")  # Debugging: Print Raw Response

            if data.get("Response") == "True":
                try:  # Handle data type errors
                    year = int(data["Year"])
                    rating = float(data["imdbRating"])
                except ValueError:
                    print("Error: Invalid data type received from OMDb API.")
                    return None

                return {
                    "title": data["Title"],
                    "year": year,
                    "rating": rating,
                    "poster": data["Poster"],
                }
            else:
                print(
                    f"Error: Movie '{title}' not found in OMDb API.  Error message: {data.get('Error')}"
                )
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error: Connection problem or timeout occurred: {e}")
            return None
        except Exception as e:  # Catch other potential errors
            print(f"An unexpected error occurred: {e}")
            return None

    def _command_list_movies(self):
        """Lists all movies in the database."""
        self.movies = self._storage.list_movies()
        print("\nListing all movies:")
        for movie, details in self.movies.items():
            print(
                f"{details['title']} - Rating: {details['rating']:.1f} - Year: {details['year']} - Poster: {details['poster']}"
            )
        print()

    def _command_add_movie(self):
        """Adds a new movie to the database using OMDb API."""
        title = input("Enter the title of the movie to add: ").strip()
        if self._storage.get_movie(title):
            print(f"{title} already exists in the List of Movies.\n")
            return

        movie_data = self._get_movie_from_omdb(title)
        if movie_data:
            self._storage.add_movie(movie_data)
            self.movies = self._storage.list_movies()  # Refresh movie list
            print(f"Movie '{title}' added successfully!\n")
        else:
            print(f"Could not retrieve movie data for '{title}'.\n")

    def _command_delete_movie(self):
        """Deletes a movie from the database."""
        title = input("Enter the title of the movie to delete: ").strip()
        if not self._storage.get_movie(title):
            print(f"Movie '{title}' not found in the database.\n")
            return

        confirmation = input(f"Are you sure you want to delete '{title}'? (y/n): ").lower()
        if confirmation == "y":
            self._storage.delete_movie(title)  # Use storage's delete_movie method
            self.movies = self._storage.list_movies()  # Refresh movie list
            print(f"Movie '{title}' deleted successfully!\n")
        else:
            print("Deletion cancelled.\n")

    def _command_update_movie(self):
        """Updates a movie in the database."""
        title = input("Enter the title of the movie to update: ").strip()
        if not self._storage.get_movie(title):
            print(f"Movie '{title}' not found in the database.\n")
            return

        print("Enter the new details (leave blank to keep the existing value):")
        new_rating_str = input("New rating: ").strip()
        new_year_str = input("New year: ").strip()
        new_poster = input("New poster URL: ").strip()

        update_data = {}
        if new_rating_str:
            try:
                update_data['rating'] = float(new_rating_str)
            except ValueError:
                print("Invalid rating format. Update skipped.")
        if new_year_str:
            try:
                update_data['year'] = int(new_year_str)
            except ValueError:
                print("Invalid year format. Update skipped.")
        if new_poster:
            update_data['poster'] = new_poster

        if update_data:
            self._storage.update_movie(title, update_data)
            self.movies = self._storage.list_movies()  # Refresh movie list
            print(f"Movie '{title}' updated successfully!\n")
        else:
            print("No updates provided.\n")

    def _command_movie_stats(self):
        """Displays statistics about the movies in the database."""
        if not self.movies:
            print("No movies available to show statistics.\n")
            return

        stats = self._storage.movie_stats()  # Get stats from storage
        for key, value in stats.items():
            print(f"{key}: {value}\n")

    def _command_random_movie(self):
        """Displays a random movie from the database."""
        if not self.movies:
            print("No movies available.\n")
            return

        random_movie_title = random.choice(list(self.movies.keys()))
        movie = self.movies[random_movie_title]
        print(f"\nRandom movie: {movie['title']} - Rating: {movie['rating']:.1f} - Year: {movie['year']} - Poster: {movie['poster']}\n")

    def _command_search_movie(self):
        """Searches for movies by title."""
        search_term = input("Enter the title (or part of the title) to search for: ").strip().lower()
        results = []
        for title, details in self.movies.items():
            if search_term in title.lower():
                results.append(details)

        if results:
            print("\nSearch results:")
            for movie in results:
                print(f"{movie['title']} - Rating: {movie['rating']:.1f} - Year: {movie['year']} - Poster: {movie['poster']}")
            print()
        else:
            print("No movies found matching your search.\n")

    def _command_movies_sorted_by_rating(self):
        """Lists movies sorted by rating in descending order."""
        if not self.movies:
            print("No movies available to sort.\n")
            return

        sorted_movies = sorted(self.movies.values(), key=lambda movie: movie['rating'], reverse=True)
        print("\nMovies sorted by rating (descending):")
        for movie in sorted_movies:
            print(f"{movie['title']} - Rating: {movie['rating']:.1f} - Year: {movie['year']} - Poster: {movie['poster']}")
        print()

    def _command_generate_website(self):
        """Generates the website based on the movie data."""
        try:
            movies = self._storage.list_movies()
            html_content = self._generate_html(movies)

            with open("website/index.html", "w", encoding="utf-8") as f:
                f.write(html_content)

            print("website was generated successfully.\n")

        except Exception as e:
            print(f"Error generating website: {e}\n")

    def _generate_html(self, movies):
        """Generates the HTML content for the website using the provided template."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>My Movie App</title>
            <link rel="stylesheet" href="style.css"/>
        </head>
        <body>
        <div class="list-movies-title">
            <h1>MY MOVIES WEBSITE</h1>
        </div>
        <div>
            <ol class="movie-grid">
                  <!-- ALL MOVIES WILL BE INSERTED HERE -->
        """

        movie_list_items = ""
        for movie_title, movie_data in movies.items():
            movie_list_items += f"""
                <li class="movie">
                    <img class="movie-poster" src="{movie_data['poster']}" alt="{movie_data['title']} Poster">
                    <div class="movie-title">{movie_data['title']}</div>
                    <div class="movie-year">{movie_data['year']}</div>
                </li>
            """

        html += movie_list_items
        html += """
            </ol>
        </div>
        </body>
        </html>
        """
        return html

    def run(self):
        """
        Main function to run the movie database application.
        """
        command_map = {
            0: "Exit",
            1: self._command_list_movies,
            2: self._command_add_movie,
            3: self._command_delete_movie,
            4: self._command_update_movie,
            5: self._command_movie_stats,
            6: self._command_random_movie,
            7: self._command_search_movie,
            8: self._command_movies_sorted_by_rating,
            9: self._command_generate_website,
        }
        self._running = True
        while self._running:
            self._print_menu()
            try:
                choice = int(input("Enter a Choice (0-9): "))  # Updated range
                if choice not in command_map:
                    print("Invalid choice. Please enter a number between 0 and 9.")  # Updated range
                    continue
                if choice == 0:
                    print("Bye!")
                    self._running = False
                    continue

                command = command_map[choice]
                command()  # Execute the command
            except ValueError:
                print("Invalid input. Please enter a number.")