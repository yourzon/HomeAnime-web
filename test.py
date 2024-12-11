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

        cursor.execute("SELECT t.Name FROM tags t JOIN manga_tags mt ON t.tag_id = mt.tag_id WHERE mt.manga_id = 'a1c7c817-4e59-43b7-9365-09675a149a6f' ;")
        rows = cursor.fetchall()
        names = [row[0] for row in rows]
        genres = ", ".join(names)
        
        # Execute the query
        #cursor.execute("SELECT * FROM manga WHERE title LIKE ?", (f'%{manga_name}%',))
        #row = cursor.fetchone()
        #print(type(names))
        print(genres)
        """
        if row:
            # Get column names
            columns = [desc[0] for desc in cursor.description]

            # Create a named tuple for the row
            MangaRow = namedtuple("MangaRow", columns)
            manga = MangaRow(*row)

            print(manga.manga_id)
        else:
            print("No results found.")
"""
        # Clean up
        cursor.close()
        connection.close()

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")

# Test the function
fetch_manga("One Piece")

