from flask import Flask, render_template, request, send_file, url_for, redirect, session, flash
from flask_mysqldb import MySQL
import requests
from collections import namedtuple
from io import BytesIO
import os
from config import TestingConfig
from mylib import *
import math

app = Flask(__name__)

app.config.from_object(TestingConfig)

mysql = MySQL(app)
STATIC_IMAGE_PATH = "static/images/no-image-401x401.webp"
STATIC_IMAGE_MIME = 'image/webp'
#TODO:
#- Add skin to manga.html and index.html (pure css or bootstrap?) more needed - DONE
#- Cleanup backend python (chatgpt) - DONE
#- make SQL connexion using os variable (app.config) - DONE
#- make SQL command more streamline - DONE
#- redo script using new name sql - DONE

#- add if up to date in manga details and search - 
#- add new entry in sql and maybe add tags? - LATER
#- add more comment to js and python code
#- add statistique page
#- add remove entry code
#- refactor with manga class like the scripts
#- refactor with sql class
#- Convert code to production

# Initiliase MariaDB class
db = MariaDBConnection(mysql)

@app.route('/proxy-image/<manga_id>')
def proxy_image(manga_id):
    """
    Fetches and serves the manga cover image from MangaDex, or a static fallback image
    if the cover image is not available, the MangaDex API call fails, or if any error occurs.
    
    This function first attempts to retrieve the manga cover image from the MangaDex API.
    If the cover image is not found or if there are any issues (e.g., no internet connection,
    missing cover art, etc.), it serves a static fallback image.

    Args:
        manga_id (str): The unique ID of the manga whose cover image is to be fetched.

    Returns:
        Flask Response: The cover image if found, or a fallback static image if an error occurs.
        The response will have the appropriate content type (e.g., image/jpeg or image/webp).
    """
    # API URL to get the manga cover art
    url = f"https://api.mangadex.org/manga/{manga_id}?includes[]=cover_art"

    try:
        # Fetch the data from the MangaDex API
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        manga_data = response.json()
    except requests.exceptions.RequestException:
        return send_file(
            os.path.join(app.root_path, STATIC_IMAGE_PATH),  # Static fallback image
            mimetype=STATIC_IMAGE_MIME
        )
    
    # Extract the cover relationship
    relationships = manga_data.get("data", {}).get("relationships", [])
    cover_relationship = next(
        (rel for rel in relationships if rel.get("type") == "cover_art"), 
        None
    )

    # If no cover art found, return the static fallback
    if not cover_relationship:
        return send_file(
            os.path.join(app.root_path, STATIC_IMAGE_PATH),  # Static fallback image
            mimetype=STATIC_IMAGE_MIME
        )

    cover_filename = cover_relationship.get("attributes", {}).get("fileName")
    
    if not cover_filename:
        return send_file(
            os.path.join(app.root_path, STATIC_IMAGE_PATH),  # Static fallback image
            mimetype=STATIC_IMAGE_MIME
        )

    # Construct the URL for the cover image
    base_url = "https://uploads.mangadex.org/covers"
    full_image_url = f"{base_url}/{manga_id}/{cover_filename}.256.jpg"

    try:
        # Fetch the image from the URL
        response = requests.get(full_image_url, stream=True)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Serve the image through the proxy
        return send_file(
            BytesIO(response.content),
            mimetype=response.headers.get('Content-Type', 'image/jpeg')  # Default to JPEG if type is not available
        )
    except requests.exceptions.RequestException:
        # If image fetch fails, return the static fallback
        return send_file(
            os.path.join(app.root_path, STATIC_IMAGE_PATH),  # Static fallback image
            mimetype=STATIC_IMAGE_MIME
        )

@app.route('/',methods=['GET'])
def index():

    session.clear()
    return render_template('index.html')

@app.route('/manga', methods=['POST'])
@app.route('/manga/<manga_id>', methods=['GET'])
def manga_handler(manga_id=None):
    """
    Handles the retrieval and display of manga details, including search by title and 
    fetching manga details by manga ID.

    This function supports two routes:
    - A POST request to `/manga` allows users to search for manga by its title. 
    - A GET request to `/manga/<manga_id>` retrieves details of a specific manga by its unique ID.

    In the case of a POST request, the manga name entered in the form is used to search for matching 
    titles in the database. If no results are found, an error message is stored in the session and 
    the user is redirected to the index page.

    For a GET request with a valid manga ID, the function retrieves the manga's details from the database.
    If no manga with the provided ID is found, a 404 error page is rendered with a message indicating 
    that the manga was not found.

    The manga details are retrieved from the database, including the manga title, description, and associated tags.
    The tags are formatted and passed to the `manga.html` template for display.

    Args:
        manga_id (str, optional): The unique ID of the manga. If not provided, the function expects
                                   a POST request to search for manga by title.

    Returns:
        flask.render_template: The rendered `manga.html` template displaying the manga's details,
                               or a 404 page if the manga is not found, or a redirect in case of an invalid search.
    """
    if request.method == 'POST':
        # Handle search by manga name
        manga_name = request.form.get('manga_name', '').strip()  # Sanitize input

        row,columns  = db.fetch_one_column("SELECT * FROM manga WHERE title LIKE %s", ('%' + manga_name + '%',))
        #columns, row = sql_command("SELECT * FROM manga WHERE title LIKE %s", ('%' + manga_name + '%',), False)

        if not row:
            # Store error in session and redirect to index
            session['error_search'] = f"Manga '{manga_name}' not found."
            return redirect(url_for('index'))

    elif request.method == 'GET':
        # Handle fetching details by manga ID from URL
        if not manga_id:
            return "Manga ID is required.", 400

        row,columns = db.fetch_one_column("SELECT * FROM manga WHERE manga_id = %s", (manga_id,))
        #columns, row = sql_command("SELECT * FROM manga WHERE manga_id = %s", (manga_id,), False)

        if not row:
            return render_template('404.html', message=f'Manga with ID {manga_id} not found.'), 404

    # Create a namedtuple based on the column names
    MangaRow = namedtuple("MangaRow", columns)
    manga = MangaRow(*row)

    # Fetch tags associated with the manga
    tags = db.fetch_all("SELECT t.Name FROM tags t JOIN manga_tags mt ON t.tag_id = mt.tag_id WHERE mt.manga_id = %s;",(manga.manga_id,))
    #tags = sql_command(
    #    "SELECT t.Name FROM tags t JOIN manga_tags mt ON t.tag_id = mt.tag_id WHERE mt.manga_id = %s;",
    #    (manga.manga_id,)
    #)

    # Convert tuples of tags to a string
    names = [tag[0] for tag in tags]
    genres = ", ".join(names)

    # Render the manga page
    return render_template('manga.html', manga_info=manga, tags=genres)

@app.route('/all', methods=['POST'])
def show_all_manga():
    """
    Fetches all manga records from the database along with their associated tags
    and renders a template to display them.

    This function queries the database to retrieve all records from the `manga` table.
    For each manga record, it also fetches associated tags from the `tags` table and
    joins them into a single string of tag names. It then combines the manga data and tags
    into a new namedtuple. The function passes the combined data (manga records and tags)
    to the `all_manga.html` template for rendering.

    The function is accessible via a POST request to the `/all` route.

    Returns:
        flask.render_template: The rendered HTML template displaying all manga records
        with their associated tags.
    """
    rows,columns = db.fetch_all_column("SELECT * FROM manga")
    
    # Remove 'eng_name' and 'is_external' from columns
    excluded_columns = {'eng_name', 'is_external'}
    filtered_columns = [col for col in columns if col not in excluded_columns]
    
    # Get column indexes that we need (excluding 'eng_name' and 'is_external')
    column_indexes = [i for i, col in enumerate(columns) if col not in excluded_columns]
    
    # Define namedtuple AFTER filtering out unwanted columns
    MangaWithTags = namedtuple("MangaWithTags", filtered_columns + ["tags"])
    
    # Create the manga list using correct column mapping
    # List comprehensions exemple
    all_manga = [
        MangaWithTags(
            **{col: row[i] for col, i in zip(filtered_columns, column_indexes)},  # Map only the correct indices
            tags=", ".join([tag[0] for tag in db.fetch_all(
                "SELECT t.Name FROM tags t JOIN manga_tags mt ON t.tag_id = mt.tag_id WHERE mt.manga_id = %s;", 
                (row[0],)
            )])
        )
        for row in rows
    ]

    # Render a template to show all manga
    return render_template('all_manga.html', manga_list=all_manga)

@app.route('/edit',methods=['GET','POST'])
def edit_sql():
    #TODO redo edit page

    if request.method == 'POST':
        action = request.form.get('action','')
        
        # Delete the manga from DB
        if action == 'delete':
            manga_id = session.get('manga_id')
            
            if 'confirm' in request.form:  # Step 2: User confirmed deletion
            
                # Check if manga has tags in manga_tags table
                row = db.fetch_all("SELECT * FROM manga_tags WHERE manga_id = %s", (manga_id,))
                
                if row: # If manga has tags, delete the entries first
                    db.delete("DELETE FROM manga_tags WHERE manga_id = %s", (manga_id,))
                    
                # Delete manga from the manga table
                result = db.delete("DELETE FROM manga WHERE manga_id = %s", (manga_id,))
                
                if result > 0:  # If result is the number of rows deleted
                    flash("Manga deleted successfully!", "delete")
                    session.pop('pending_delete', None)  # Clear the pending delete session data
                    return redirect(url_for('edit_sql',action='cancel'))
                else:
                    flash("Manga deletion failed. No rows affected.", "delete")
                    return render_template('edit.html')
            
            # Step 1: Fetch manga details and ask for confirmation
            row, columns = db.fetch_one_column("SELECT * FROM manga WHERE manga_id = %s", (manga_id,))
            
            if row:
                MangaRow = namedtuple("MangaRow", columns)
                manga = MangaRow(*row)
                session['pending_delete'] = manga_id  # Store manga ID for confirmation
                flash(f"Are you sure you want to delete: {manga.manga_id}, {manga.title}, {manga.eng_name}?", "warning")
                return render_template('edit.html')
                
        elif action == 'info':
            manga_id = request.form.get('manga_id', '').strip()
            valid_entry = db.fetch_one("SELECT 1 FROM manga WHERE manga_id = %s", (manga_id,)) is not None

            # Store the result in session
            session['valid_entry'] = valid_entry
            session['manga_id'] = manga_id
            
            # If invalid, set error message in session and render template
            if not valid_entry:
                session['error'] = "Invalid Manga ID"
                return render_template('edit.html')
            
            # Get colums name for dropdown menu
            columns_names = db.fetch_all("""
                            SELECT COLUMN_NAME
                            FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_NAME ="manga";
                            """)
            options = [{'value': col, 'label': col} for col in (col[0] for col in columns_names) if col != "manga_id"]
            session['options']= options
            
            return render_template('edit.html',options=options)
        
        elif action == 'update':
            options = session.get('options')
            manga_id= session.get('manga_id')
            # Get dropdown choice 
            selected_option  = request.form.get('dropdown','')
            # Get value entered
            input_field = request.form.get('inputField','')
            # send it and check if error comme back
            print(selected_option,input_field)
            print(f"UPDATE manga SET {selected_option} = %s WHERE manga_id = %s", (input_field, manga_id))

            result = db.update(f"UPDATE manga SET {selected_option} = %s WHERE manga_id = %s", (input_field, manga_id))
            print(session)
            print(result)
            
            if isinstance(result, str) and 'Error' in result:
                flash(result, "update")  # Flash the error message
            else:
                flash("The last modification was a success!", "update")  # Flash success message

            return render_template('edit.html', options=options)
                        

        
       
    
    if request.method == 'GET':
        # Clear session if the cancel button was clicked
        if request.args.get('action') == 'cancel':
            session.pop('valid_entry', None)
            session.pop('manga_id', None)
            session.pop('error', None)
            session.pop('success', None)

        return render_template('edit.html')


#TODO
@app.route('/statistiques',methods=['GET'])
def get_stats():
    #TODO remake css page
        
    # The quantity of manga by status_read
    status_read = db.fetch_all("""
        SELECT status_read, COUNT(*) as quantity
        FROM manga 
        GROUP BY status_read 
        ORDER BY quantity DESC
        """)
    # The quantity of manga by year of release
    year_release = db.fetch_all("""
        SELECT year_release AS release_year, COUNT(*) AS quantity
        FROM manga
        GROUP BY year_release
        ORDER BY year_release DESC;
    """)
    # The quantity of tags
    tags_stats = db.fetch_all("""
        SELECT t.name, COUNT(mt.tag_id) AS tag_count
        FROM tags t
        JOIN manga_tags mt ON t.tag_id = mt.tag_id
        GROUP BY t.name
        ORDER BY tag_count DESC;
    """)
    status_offi = db.fetch_all("""
        SELECT status_offi, COUNT(*) as quantity
        FROM manga 
        GROUP BY status_offi 
        ORDER BY quantity DESC
        """)
    
    # Fetch values from the database
    single_stats = {
        # Quantity of manga
        "number_manga" :  db.fetch_one("SELECT COUNT(*) FROM manga")[0],
        # Average of chapter read
        "average_chapter" : math.ceil(db.fetch_one("SELECT AVG(chapter_read) FROM manga")[0] or 0),
        # The quantity of active is_latest 
        "is_latest" : db.fetch_one("SELECT COUNT(*) FROM manga WHERE is_latest = 1")[0]
    }
    
    return render_template('statistiques.html',stats = single_stats, 
                           status_read = status_read, year_release = year_release,
                           tags_stats = tags_stats, status_offi =  status_offi
                           )

if __name__ == '__main__':
    app.run(debug=True)