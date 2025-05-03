import os
import requests
import random



class MovieApp:
    def __init__(self, storage, template_folder='templates'):
        """
        Initializes the MovieApp with a storage object and template folder.

        Args:
            storage: An object implementing the storage interface (like StorageCsv).
            template_folder (str): The path to the folder containing HTML templates.
        """
        self._storage = storage
        self.movies = {}  # Initialize empty, load on demand or here
        self._running = True
        self.omdb_api_key = os.environ.get("OMDB_API_KEY") or "4d55412d"  # Get API key or fallback

        # Load initial movies
        self._load_initial_movies()

        if not self.omdb_api_key:
            print(
                "Warning: OMDB_API_KEY not found in environment variables. Add movie functionality will be limited.")

        # ---  Setup ---
        self.template_folder = template_folder
        # Create the template directory if it doesn't exist
        os.makedirs(self.template_folder, exist_ok=True)

    def _load_initial_movies(self):
        """Loads movies from storage during initialization."""
        try:
            self.movies = self._storage.list_movies()
        except Exception as e:
            print(f"Error loading initial movies from storage: {e}")
            self.movies = {}  # Ensure movies is a dict even if loading fails

    def _refresh_movies_from_storage(self):
        """Reloads the movie list from the storage."""
        try:
            self.movies = self._storage.list_movies()
        except Exception as e:
            print(f"Error refreshing movies from storage: {e}")
            # Decide if you want to clear self.movies or keep the old ones

    def _print_menu(self):
        """Prints the available menu options."""
        print("\n********** My Movies Database **********")
        print("\nMenu:")
        menu_options = [
            "Exit",  # 0
            "List Movies",  # 1
            "Add Movie",  # 2
            "Delete Movie",  # 3
            "Update Movie",  # 4
            "Stats",  # 5
            "Random movie",  # 6
            "Search movie",  # 7
            "Movies sorted by rating",  # 8
            "Generate website",  # 9
        ]
        for index, option in enumerate(menu_options):
            print(f"{index}. {option}")
        print("-" * 40)  # Wider separator

    def _get_movie_from_omdb(self, title):
        """Fetches movie data from OMDb API. Returns a dict or None."""
        if not self.omdb_api_key:
            print("Error: OMDB_API_KEY is not set. Cannot fetch movie data.")
            return None

        try:
            # Basic sanitization of title for URL
            safe_title = requests.utils.quote(title)
            url = f"http://www.omdbapi.com/?t={safe_title}&apikey={self.omdb_api_key}"
            # print(f"DEBUG: API URL: {url}") # Uncomment for debugging

            response = requests.get(url, timeout=10)  # Set a reasonable timeout
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            data = response.json()
            # print(f"DEBUG: Raw JSON response: {data}") # Uncomment for debugging

            if data.get("Response") == "True":
                # More robust data extraction and type conversion
                try:
                    # Handle potential year ranges like "2008–2013" or just "2008"
                    year_str = data.get("Year", "0")
                    # Take only the first part if it's a range, remove non-digits
                    year_part = ''.join(filter(str.isdigit, year_str.split('–')[0]))
                    year = int(year_part) if year_part else 0  # Default to 0 if parsing fails

                    rating_str = data.get("imdbRating", "N/A")
                    # Convert to float, handle "N/A"
                    rating = float(rating_str) if rating_str != "N/A" else 0.0

                    poster = data.get("Poster", "")  # Get poster, default to empty string
                    # Optionally check if poster URL seems valid (basic check)
                    if poster == "N/A":
                        poster = ""

                    # Ensure title exists
                    fetched_title = data.get("Title", "").strip()
                    if not fetched_title:
                        print(
                            f"Warning: OMDb returned movie data without a title for query '{title}'. Skipping.")
                        return None

                    return {
                        "title": fetched_title,
                        "year": year,
                        "rating": rating,
                        "poster": poster,
                    }
                except (ValueError, TypeError) as e:
                    print(
                        f"Error: Invalid data type received from OMDb API for '{title}': {e}. Data: {data}")
                    return None
            else:
                error_message = data.get('Error', 'Unknown error')
                print(f"Error: Movie '{title}' not found in OMDb. Message: {error_message}")
                return None

        except requests.exceptions.Timeout:
            print(f"Error: Request to OMDb API timed out for '{title}'.")
            return None
        except requests.exceptions.RequestException as e:
            # This catches connection errors, DNS errors, invalid responses, etc.
            print(f"Error: Network problem or issue connecting to OMDb API: {e}")
            return None
        except Exception as e:  # Catch other potential errors during processing
            print(f"An unexpected error occurred during OMDb fetch for '{title}': {e}")
            return None

    def _command_list_movies(self):
        """Lists all movies currently loaded in the app."""
        self._refresh_movies_from_storage()  # Ensure we have the latest data
        if not self.movies:
            print("\nThe movie database is empty.\n")
            return

        print("\n--- Movie List ---")
        # Sort by title for consistent listing
        for title in sorted(self.movies.keys()):
            details = self.movies.get(title, {})  # Use .get for safety
            # Format output nicely, handling potentially missing data
            rating_str = f"{details.get('rating', 0.0):.1f}" if isinstance(details.get('rating'),
                                                                            (int, float)) else "N/A"
            year_str = str(details.get('year', 'N/A'))
            poster_str = "Yes" if details.get('poster') else "No"

            print(f"- {details.get('title', title)} "
                  f"(Rating: {rating_str}, Year: {year_str}, Poster: {poster_str})")
        print("-" * 18 + "\n")

    def _command_add_movie(self):
        """Prompts user, fetches from OMDb, and adds a movie to storage."""
        title = input("Enter the title of the movie to add: ").strip()
        if not title:
            print("Movie title cannot be empty.\n")
            return

        # Check if already exists (consider case-insensitivity for robustness)
        self._refresh_movies_from_storage()  # Check against latest data
        if title in self.movies:  # Basic case-sensitive check
            print(f"Movie '{title}' already exists in the database.\n")
            return
        # Optional: Case-insensitive check
        # if any(t.lower() == title.lower() for t in self.movies.keys()):
        #      print(f"Movie similar to '{title}' already exists (case-insensitive match).")
        #      # Decide whether to proceed or stop

        print(f"\nSearching OMDb for '{title}'...")
        movie_data = self._get_movie_from_omdb(title)

        if movie_data:
            # Double-check if the fetched title already exists (API might return slightly different casing)
            fetched_title = movie_data.get('title')
            if fetched_title and fetched_title in self.movies:
                print(f"Movie '{fetched_title}' (returned by OMDb) already exists.\n")
                return

            try:
                self._storage.add_movie(movie_data)  # Let storage handle saving
                self._refresh_movies_from_storage()  # Update internal list
                print(f"Movie '{movie_data.get('title', title)}' added successfully!\n")
            except Exception as e:
                print(f"Error saving movie '{title}' to storage: {e}\n")
        else:
            # Error message already printed by _get_movie_from_omdb
            print(f"Could not add movie '{title}'. See previous errors for details.\n")

    def _command_delete_movie(self):
        """Prompts user and deletes a movie from storage."""
        self._refresh_movies_from_storage()  # Ensure we check against current data
        if not self.movies:
            print("Movie database is empty, nothing to delete.\n")
            return

        title = input("Enter the exact title of the movie to delete: ").strip()
        if not title:
            print("Movie title cannot be empty.\n")
            return

        # Verify existence before asking for confirmation
        if title not in self.movies:
            print(f"Movie '{title}' not found in the database.\n")
            return

        try:
            # Confirmation dialog
            confirmation = input(f"Are you sure you want to delete '{title}'? (y/n): ").lower().strip()
            if confirmation == "y":
                self._storage.delete_movie(title)  # Tell storage to delete
                self._refresh_movies_from_storage()  # Update internal list
                print(f"Movie '{title}' deleted successfully.\n")
            else:
                print("Deletion cancelled.\n")
        except Exception as e:
            print(f"Error deleting movie '{title}' from storage: {e}\n")

    def _command_update_movie(self):
        """Prompts user for title and updates movie details in storage."""
        self._refresh_movies_from_storage()  # Get latest data
        if not self.movies:
            print("Movie database is empty, nothing to update.\n")
            return

        title = input("Enter the exact title of the movie to update: ").strip()
        if not title:
            print("Movie title cannot be empty.\n")
            return

        movie_to_update = self.movies.get(title)  # Use .get for safety
        if not movie_to_update:
            print(f"Movie '{title}' not found in the database.\n")
            return

        print(f"\nCurrent details for '{title}':")
        print(f"  Rating: {movie_to_update.get('rating', 'N/A')}")
        print(f"  Year: {movie_to_update.get('year', 'N/A')}")
        print(f"  Poster URL: {movie_to_update.get('poster', 'N/A')}")
        print("\nEnter new details (leave blank to keep existing value):")

        update_data = {}
        try:
            # Update Rating
            new_rating_str = input(f"  New rating [{movie_to_update.get('rating', 'N/A')}]: ").strip()
            if new_rating_str:
                update_data['rating'] = float(new_rating_str)

            # Update Year
            new_year_str = input(f"  New year [{movie_to_update.get('year', 'N/A')}]: ").strip()
            if new_year_str:
                update_data['year'] = int(new_year_str)

            # Update Poster URL
            # Provide explicit instruction on how to clear it if needed
            current_poster = movie_to_update.get('poster', '')
            poster_prompt = f"  New poster URL [{current_poster if current_poster else 'None'}]: "
            new_poster = input(poster_prompt).strip()
            # Only update if *any* non-empty string is entered
            if new_poster:  # Update if *any* non-empty string is entered
                update_data['poster'] = new_poster
            # No else needed, if blank, update_data['poster'] is not set

        except ValueError as e:
            print(f"Invalid input: {e}. Please enter numbers for rating/year. Update cancelled.\n")
            return

        if update_data:
            try:
                self._storage.update_movie(title, update_data)  # Tell storage to update
                self._refresh_movies_from_storage()  # Refresh internal list
                print(f"Movie '{title}' updated successfully!\n")
            except Exception as e:
                print(f"Error updating movie '{title}' in storage: {e}\n")
        else:
            print("No changes provided. Update cancelled.\n")

    def _command_movie_stats(self):
        """Calculates and displays statistics using the storage method."""
        self._refresh_movies_from_storage()  # Use latest data
        if not self.movies:
            print("No movies available to calculate statistics.\n")
            return

        try:
            # Delegate calculation to storage - assumes storage implements movie_stats()
            stats = self._storage.movie_stats()

            print("\n--- Movie Statistics ---")
            if stats:
                # Example: Assuming stats is a dict like {"Average Rating": 7.5, "Count": 10}
                print(f"Total Movies: {stats.get('Count', len(self.movies))}")  # Use count from stats if available

                avg_rating = stats.get("Average Rating")
                if isinstance(avg_rating, (int, float)):
                    print(f"Average Rating: {avg_rating:.2f}")
                else:
                    print(f"Average Rating: {avg_rating if avg_rating is not None else 'N/A'}")

                # Add more stats as returned by storage.movie_stats()
                # median = stats.get("Median Rating") etc.

            else:
                # Handle case where storage returns None or empty dict
                print("Could not retrieve statistics from storage.")
            print("-" * 24 + "\n")

        except AttributeError:
            print("Error: The storage object does not support the 'movie_stats' method.\n")
        except Exception as e:
            print(f"Error calculating movie statistics: {e}\n")

    def _command_random_movie(self):
        """Selects and displays a random movie."""
        self._refresh_movies_from_storage()  # Use latest data
        if not self.movies:
            print("No movies available to select a random one.\n")
            return

        try:
            random_movie_title = random.choice(list(self.movies.keys()))
            movie = self.movies[random_movie_title]

            print("\n--- Random Movie ---")
            print(f"Title:  {movie.get('title', 'N/A')}")
            rating_str = f"{movie.get('rating', 0.0):.1f}" if isinstance(movie.get('rating'),
                                                                            (int, float)) else "N/A"
            print(f"Rating: {rating_str}")
            print(f"Year:   {movie.get('year', 'N/A')}")
            print(f"Poster: {movie.get('poster', 'N/A')}")
            print("-" * 20 + "\n")
        except IndexError:  # Should not happen if self.movies check passes, but good practice
            print("Error: Could not select a random movie (list might be empty unexpectedly).\n")
        except Exception as e:
            print(f"Error selecting or displaying random movie: {e}\n")

    def _command_search_movie(self):
        """Searches for movies by title substring (case-insensitive)."""
        self._refresh_movies_from_storage()  # Use latest data
        if not self.movies:
            print("No movies available to search.\n")
            return

        search_term = input("Enter part of the movie title to search for: ").strip().lower()
        if not search_term:
            print("Search term cannot be empty.\n")
            return

        results = []
        for title, details in self.movies.items():
            # Case-insensitive search in the movie title
            if search_term in title.lower():
                results.append(details)

        if results:
            print(f"\n--- Search Results for '{search_term}' ({len(results)} found) ---")
            # Sort results alphabetically by title for clarity
            results.sort(key=lambda m: m.get('title', '').lower())
            for movie in results:
                rating_str = f"{movie.get('rating', 0.0):.1f}" if isinstance(movie.get('rating'),
                                                                                (int, float)) else "N/A"
                year_str = str(movie.get('year', 'N/A'))
                print(f"- {movie.get('title', 'N/A')} (Rating: {rating_str}, Year: {year_str})")
            print("-" * (30 + len(search_term)) + "\n")
        else:
            print(f"No movies found matching '{search_term}'.\n")

    def _command_movies_sorted_by_rating(self):
        """Lists movies sorted by rating (descending)."""
        self._refresh_movies_from_storage()  # Use latest data
        if not self.movies:
            print("No movies available to sort.\n")
            return

        try:
            # Filter out movies that might not have a valid numeric rating
            valid_movies = [
                m for m in self.movies.values() if isinstance(m.get('rating'), (int, float))
            ]

            if not valid_movies:
                print("No movies with valid ratings found to sort.\n")
                return

            # Sort by rating (descending), then by title (ascending) as a tie-breaker
            sorted_movies = sorted(
                valid_movies,
                key=lambda movie: (-movie.get('rating', -1.0), movie.get('title', '').lower())
            )

            print("\n--- Movies Sorted by Rating (Highest First) ---")
            for movie in sorted_movies:
                rating_str = f"{movie.get('rating', 0.0):.1f}"  # Already checked it's a float/int
                year_str = str(movie.get('year', 'N/A'))
                print(f"- {movie.get('title', 'N/A')} (Rating: {rating_str}, Year: {year_str})")
            print("-" * 45 + "\n")

        except Exception as e:
            print(f"Error sorting movies by rating: {e}\n")

    def _command_generate_website(self):
        """Generates a website displaying the movie collection."""
        self._refresh_movies_from_storage()
        if not self.movies:
            print("No movies available to generate a website.\n")
            return

        try:
            # 1. Generate the main index.html
            self._generate_index_html()

            print(f"Website generated successfully in {self.template_folder}\n")

        except Exception as e:
            print(f"Error generating website: {e}\n")

    def _generate_index_html(self):
        """Generates the main final_index.html file."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>My Movie App</title>
            <link rel="stylesheet" href="style.css">
        </head>
        <body>
            <div class="list-movies-title">
                <h1>My Movie Collection</h1>
            </div>
            <ul class="movie-grid">
        """

        for title, movie in sorted(self.movies.items()):  # Sort movies by title
            poster = movie.get('poster', '')
            movie_title = movie.get('title', title)
            year = movie.get('year', 'N/A')
            rating = movie.get('rating', 'N/A')

            html_content += f"""
                <li class="movie-item">
                    <div class="movie">
                        {'<img class="movie-poster" src="{}" alt="{} Poster">'.format(poster, movie_title) if poster else '<div class="no-poster">No Poster Available</div>'}
                        <h2 class="movie-title">{movie_title}</h2>
                        <p class="movie-year">Year: {year}</p>
                        <p>Rating: {rating}</p>
                    </div>
                </li>
            """

        html_content += """
            </ul>
        </body>
        </html>
        """

        output_path = os.path.join(self.template_folder, 'final_index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def run(self):
        """
        Main application loop: displays menu, gets user choice, executes command.
        """
        # Command map: maps choice number to (Display Name, function_to_call)
        command_map = {
            0: ("Exit", lambda: setattr(self, '_running', False)),  # Use lambda to modify state
            1: ("List Movies", self._command_list_movies),
            2: ("Add Movie", self._command_add_movie),
            3: ("Delete Movie", self._command_delete_movie),
            4: ("Update Movie", self._command_update_movie),
            5: ("Stats", self._command_movie_stats),
            6: ("Random movie", self._command_random_movie),
            7: ("Search movie", self._command_search_movie),
            8: ("Movies sorted by rating", self._command_movies_sorted_by_rating),
            9: ("Generate website", self._command_generate_website),
        }

        self._running = True
        print("Welcome to the Movie App!")

        while self._running:
            self._print_menu()
            try:
                choice_str = input("Enter Choice (0-9): ").strip()

                # Input validation
                if not choice_str.isdigit():
                    print("\nInvalid input: Please enter a number.")
                    continue  # Ask for input again

                choice = int(choice_str)

                if choice in command_map:
                    action_name, action_func = command_map[choice]

                    if action_name == "Exit":
                        print("\nBye!")
                        action_func()  # Sets self._running to False
                    else:
                        print(f"\n--- Executing: {action_name} ---")
                        action_func()  # Call the corresponding command method
                        # Pause after command execution (except for Exit)
                        input("\nPress Enter to return to menu...")
                else:
                    print("\nInvalid choice. Please enter a number between 0 and 9.")

            except ValueError:  # Should be caught by isdigit, but belt-and-suspenders
                print("\nInvalid input: Please enter a number.")
            except KeyboardInterrupt:  # Handle Ctrl+C gracefully
                print("\n\nExiting application due to user interrupt.")
                self._running = False
            except Exception as e:  # Generic catch for unexpected errors within a command
                print(f"\n*** An unexpected error occurred: {e} ***")
                print("*** Please report this issue. ***")
                # Consider logging the full traceback here for debugging
                # import traceback
                # traceback.print_exc()
                input("\nPress Enter to try returning to menu...")

        print("\nApplication finished.")


class ListMovieTitles:
    """
    A class for displaying movie titles in a list format.
    """

    def __init__(self, movies):
        """
        Initializes the ListMovieTitles object with a dictionary of movies.

        Args:
            movies (dict): A dictionary where keys are movie titles and values are movie details.
        """
        self.movies = movies

    def generate_html(self):
        """
        Generates an HTML unordered list of movie titles.

        Returns:
            str: An HTML string representing the list of movie titles.
        """
        html = "<ul>\n"
        for title in sorted(self.movies.keys()):
            movie = self.movies[title]
            html += f"  <li>{movie.get('title', title)}</li>\n"
        html += "</ul>\n"
        return html


class MovieGrid:
    """
    A class for displaying movies in a grid format, including posters.
    """

    def __init__(self, movies):
        """
        Initializes the MovieGrid object with a dictionary of movies.

        Args:
            movies (dict): A dictionary where keys are movie titles and values are movie details.
        """
        self.movies = movies

    def generate_html(self):
        """
        Generates an HTML grid of movie posters and titles.

        Returns:
            str: An HTML string representing the movie grid.
        """
        html = '<div class="movie-grid">\n'
        for title, movie in sorted(self.movies.items()):  # Sort movies by title
            poster_url = movie.get('poster', '')
            movie_title = movie.get('title', title)

            html += '  <div class="movie-item">\n'
            if poster_url:
                html += f'    <img src="{poster_url}" alt="{movie_title} Poster">\n'
            else:
                html += f'    <div class="no-poster">No Poster Available</div>\n'
            html += f'    <p>{movie_title}</p>\n'
            html += '  </div>\n'
        html += '</div>\n'
        return html

    def _slugify(self, title):
        """Converts a movie title into a URL-friendly slug."""
        slug = title.lower().replace(" ", "-")
        slug = ''.join(char for char in slug if char.isalnum() or char == '-')
        return slug