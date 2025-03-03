# My Movie App - OOP + Web

## Overview

This project is a simple movie database application built using Python with an Object-Oriented Programming (OOP) approach. It allows users to manage a collection of movies, view statistics, search for movies, and generate a basic HTML website to display their movie list. The application stores movie data in a CSV file for persistence and leverages the OMDB API to fetch movie details.

## Features

*   **Add Movie:** Add new movies to the database, fetching details from the OMDB API.
*   **List Movies:** Display all movies in the database with details (title, rating, year, poster URL).
*   **Delete Movie:** Remove movies from the database.
*   **Update Movie:** Modify existing movie details (rating, year, poster URL).
*   **Stats:** Calculate and display statistics like average rating.
*   **Random Movie:** Select and display a random movie from the database.
*   **Search Movie:** Search for movies by title (or partial title).
*   **Sort by Rating:** Display movies sorted by rating in descending order.
*   **Generate Website:** Create a basic HTML website (`index.html`) displaying the movie list, styled with CSS.

## Technologies Used

*   **Python:** The primary programming language.
*   **Object-Oriented Programming (OOP):** Used to structure the application with classes for data storage and application logic.
*   **CSV (Comma-Separated Values):** Used to store movie data persistently in a file.
*   **requests:** A Python library used to make HTTP requests to the OMDB API.
*   **dotenv:** A Python library used to load environment variables from a `.env` file.
*   **OMDB API (Open Movie Database):** A web service API used to fetch movie details (title, year, rating, poster URL).
*   **HTML/CSS:** Used to generate the website (`index.html`) and style it.

## Project Structure




## Setup Instructions

1.  **Clone the repository:**

    ```bash
    git clone [repository URL]
    cd [project directory]
    ```

2.  **Install dependencies:**

    ```bash
    pip install requests python-dotenv
    ```

3.  **Obtain an OMDB API Key:**

    *   Register on the OMDB website ([https://www.omdbapi.com/](https://www.omdbapi.com/)) to obtain a free API key.

4.  **Set the OMDB API Key:**

    *   **Option 1: Environment Variable:** Set an environment variable named `OMDB_API_KEY` with your API key.  How to set environment variables depends on your operating system (see previous responses for detailed instructions).

    *   **Option 2: `.env` File:** Create a file named `.env` in the project root directory and add the following line, replacing `YOUR_API_KEY` with your actual API key:

        ```
        OMDB_API_KEY="YOUR_API_KEY"
        ```

        **Important:** Add `.env` to your `.gitignore` file to prevent accidentally committing your API key to a public repository.

5.  **Run the application:**

    ```bash
    python main.py
    ```

## Usage

After running the application, you'll see a menu with several options:

*   Enter the corresponding number for the desired action.  Follow the prompts in the console to add, delete, update, search, or view movie data.
*   To generate the website, select the "Generate Website" option.  This will create an `index.html` file in the same directory, which you can open in your web browser.

## Key Classes

*   **`MovieApp` (movie_app.py):**  The main application class.  It:
    *   Initializes the storage mechanism (`StorageCsv`).
    *   Provides a menu-driven interface for users to interact with the movie database.
    *   Fetches movie data from the OMDB API.
    *   Generates the HTML website.

*   **`StorageCsv` (storage_csv.py):**  Handles the storage of movie data in a CSV file.  It implements methods to:
    *   Load movies from the CSV file.
    *   Save movies to the CSV file.
    *   Add, delete, update, and retrieve movie data.
    *   Calculate movie statistics.

## Customization

*   **HTML/CSS:** Customize the `_generate_html` function in `movie_app.py` and the `style.css` file to change the appearance of the generated website.
*   **CSV File:** The name of the CSV file can be configured in the `main.py` file when instantiating the `StorageCsv` class.
*   **OMDB API Logic:**  The `_get_movie_from_omdb` function can be modified to fetch additional data from the OMDB API or to handle different API responses.

## Future Enhancements

*   Implement a more sophisticated website with dynamic content updates, JavaScript interactivity, and responsive design.
*   Add a GUI (Graphical User Interface) using a library like Tkinter, PyQt, or Kivy.
*   Use a database (e.g., SQLite, PostgreSQL) instead of a CSV file for more robust data storage and retrieval.
*   Add more advanced search and filtering capabilities.
*   Implement user authentication and authorization.
*   Improve error handling and logging.
*   Add Unit Tests.
