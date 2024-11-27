import mariadb
from collections import namedtuple

# Database connection configuration
config = {
    'host': '127.0.0.1',
    'user': 'test',
    'password': 'password',
    'database': 'mangaweb'
}

def fetch_manga(manga_name):
    try:
        # Establish database connection
        connection = mariadb.connect(**config)
        cursor = connection.cursor()

        # Execute the query
        cursor.execute("SELECT * FROM manga WHERE name LIKE %s", (f'%{manga_name}%',))
        row = cursor.fetchone()

        if row:
            # Get column names
            columns = [desc[0] for desc in cursor.description]

            # Create a named tuple for the row
            MangaRow = namedtuple("MangaRow", columns)
            manga = MangaRow(*row)

            print(manga.id_manga)
        else:
            print("No results found.")

        # Clean up
        cursor.close()
        connection.close()

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")

# Test the function
fetch_manga("One Piece")