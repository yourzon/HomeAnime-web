from flask import Flask, render_template, request, send_file, url_for, redirect, session
from flask_mysqldb import MySQL
import requests
import secrets
from collections import namedtuple
from io import BytesIO

app = Flask(__name__)

# Configure MariaDB connection
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'test'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'mangaweb'

app.secret_key = secrets.token_hex(16)

mysql = MySQL(app)
STATIC_IMAGE = "/static/images/no-image-full-detail.webp"

#TODO:
#- Add skin to manga.html and index.html (pure css or bootstrap?) more needed
#- Cleanup backend python
#- add a way to edit SQL entry (later)
#- add more comment to js and python code
#- make SQL connexion using os variable (app.config)
#- make SQL command more streamline - DONE
#- add if up to date in manga details and search
#- add new entry in sql and maybe add tags?
#- redo script using new name sql
"""
manga_id (varchar)
title (varchar)
eng_name (varchar)
chapter_read (double)
status_read (enum)
status_offi (varchar)
year_release (int)
is_latest (true/false)
tags 
"""


def get_image_url(manga_id):
    """This function get the manga cover from mangadex and
    host the image trought a local proxy or send static image.

    Args:
        manga_id (str): the unique UUID of the manga wanted

    Returns:
        str: The proxied URL or a static fallback image URL.
    """
    # API URL to get the chapter details (images)
    url = f"https://api.mangadex.org/manga/{manga_id}?includes[]=cover_art"

    try:
        # Fetch the data from the MangaDex API
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        return STATIC_IMAGE
    
    manga_data = response.json()
    # Extract cover_art relationship using next()
    cover_relationship = next(
        (rel for rel in manga_data.get("data", {}).get("relationships", []) 
         if rel.get("type") == "cover_art"),
        None
    )
   
    # Fallback if no cover_art is found
    if not cover_relationship or "attributes" not in cover_relationship:
        return STATIC_IMAGE

    cover_filename = cover_relationship["attributes"].get("fileName")
    if not cover_filename:
        return STATIC_IMAGE
   
    # Create URL to get the image from managdex server
    base_url = "https://uploads.mangadex.org/covers"
    full_image_url = f"{base_url}/{manga_id}/{cover_filename}.256.jpg"
    
    proxy_url = url_for('proxy_image', manga_id=manga_id) +f"?image_url={full_image_url}"
    
    return proxy_url
    

def sql_command(query,params=None,fetch_all=True):
    """
    Executes any SQL command and returns the result.

    Args:
        query (str): The SQL query to execute (SELECT, INSERT, UPDATE, DELETE, etc.)
        params (tuple, optional): Parameters to be used in the query. Defaults to None.
        fetch_all (bool, optional): Whether to fetch all rows (for SELECT queries). Defaults to True.

    Returns:
        tuple: For SELECT queries, returns a tuple (columns, result).
        int: For non-SELECT queries, returns the number of affected rows.
    """
    try:
        with mysql.connection.cursor() as cur:
            # Execute the query with parameters if provided
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            
            # If the query is a SELECT, fetch the results
            if query.strip().lower().startswith("select"):
                columns = [col[0] for col in cur.description]  # Column names
                if fetch_all:
                    result = cur.fetchall()  # Fetch all rows
                else:
                    result = cur.fetchone()  # Fetch only the first row
                return columns, result
            
            # For INSERT, UPDATE, DELETE, etc., commit changes and return the number of rows affected
            mysql.connection.commit()
            return cur.rowcount
    
    except Exception as e:
        # Log error message for better debugging (you can use a logger here)
        print(f"SQL Command Error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_manga_name():
    manga_name = request.form.get('manga_name', '').strip()  # Sanitize input, ensuring it's a non-empty string
    
    columns,row = sql_command("SELECT * FROM manga WHERE title LIKE %s", ('%' + manga_name + '%',),False)

    if not row:
        # Store error in session and redirect to index
        session['error_search'] = f"Manga '{manga_name}' not found."
        return redirect(url_for('index'))

    # Create a namedtuple based on the column names
    MangaRow = namedtuple("MangaRow", columns)
    manga = MangaRow(*row)

    image_url = get_image_url(manga.manga_id)
    
    # Render the manga page with the proxy URL
    return render_template('manga.html', manga_info=manga, image_url=image_url)


@app.route('/manga/<manga_id>')
def manga_details(manga_id):
    # Fetch manga details by ID from the database
    columns,row = sql_command("SELECT * FROM manga WHERE manga_id = %s", (manga_id,),False)
    
    if not row:
        return "Manga not found."
    
    # Create a namedtuple based on the column names and return the data
    MangaRow = namedtuple("MangaRow", columns)
    manga = MangaRow(*row)
    
    image_url = get_image_url(manga_id)
    
    return render_template('manga.html', manga_info=manga, image_url=image_url)


@app.route('/proxy-image/<manga_id>')
def proxy_image(manga_id):
    # fetch image_url from url paramater
    image_url = request.args.get('image_url')

    try:
        # Fetch the image from the URL
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Serve the image through the proxy
        return send_file(
            BytesIO(response.content),
            mimetype=response.headers.get('Content-Type', 'image/jpeg')  # Default to JPEG
        )
    except requests.exceptions.RequestException as e:
        return f"Error fetching image: {e}", 500


@app.route('/all', methods=['POST'])
def show_all_manga():
    
    columns,rows = sql_command("SELECT * FROM manga")
    
    # Create a namedtuple based on the column names and return the data
    MangaRows = namedtuple("MangaRow", columns)
    all_manga = [MangaRows(*row) for row in rows]
    
    # Render a template to show all manga
    return render_template('all_manga.html', manga_list=all_manga, columns=columns)

if __name__ == '__main__':
    app.run(debug=True)