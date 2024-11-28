from flask import Flask, render_template, request, send_file, url_for
from flask_mysqldb import MySQL
import requests
from collections import namedtuple
from io import BytesIO

app = Flask(__name__)

# Configure MariaDB connection
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'test'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'mangaweb'

mysql = MySQL(app)
static_image = "/static/images/no_image.png"

#TODO:
#- Add skin to manga.html and index.html (pure css or bootstrap?) more needed
#- Cleanup backend python
#- add a way to edit SQL entry (later)
#- add more comment to js and python code
#- make SQL connexion using os variable
#- make SQL command more streamline
#-

def get_image_url(manga_id):
        # API URL to get the chapter details (images)
    url = f"https://api.mangadex.org/manga/{manga_id}"

    try:
        # Fetch the data from the MangaDex API
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        return static_image
    
    manga_data = response.json()
    
    for relationship in manga_data['data']['relationships']:
        if relationship['type'] == 'cover_art':
            cover_art_id = relationship['id']
            break
    
    try:
        cover_url = f"https://api.mangadex.org/cover/{cover_art_id}"
        response = requests.get(cover_url)
        cover_response = response.json()
        file_name = cover_response["data"]["attributes"]["fileName"]
        
        base_url = "https://uploads.mangadex.org/covers"
        full_image_url = f"{base_url}/{manga_id}/{file_name}.256.jpg"
        
        proxy_url = url_for('proxy_image', manga_id=manga_id) +f"?image_url={full_image_url}"
        
        return proxy_url
    except requests.exceptions.RequestException as e:
        return f"Error fetching image: {e}", 500
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_manga():
    manga_name = request.form['manga_name']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM manga WHERE name LIKE %s", ('%' + manga_name + '%',))
    row = cursor.fetchone()

    if not row:
        cursor.close()
        return "Manga not found."
    
    # Get column names from the cursor
    columns = [col[0] for col in cursor.description]
    cursor.close()

    # Create a namedtuple based on the column names and return the data
    MangaRow = namedtuple("MangaRow", columns)
    manga = MangaRow(*row)

    image_url = get_image_url(manga.id_manga)
    
    # Render the manga page with the proxy URL
    return render_template('manga.html', manga=manga, image_url=image_url)


@app.route('/manga/<manga_id>')
def manga_details(manga_id):
    
    # Fetch manga details by ID from the database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM manga WHERE id_manga = %s", (manga_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.close()
        return "Manga not found."
    
    # Get column names from the cursor
    columns = [col[0] for col in cursor.description]
    cursor.close()

    # Create a namedtuple based on the column names and return the data
    MangaRow = namedtuple("MangaRow", columns)
    manga = MangaRow(*row)
    
    image_url = get_image_url(manga_id)
    
    return render_template('manga.html', manga=manga, image_url=image_url)


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
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM manga")
    rows = cursor.fetchall()
    # Get column names from the cursor
    columns = [col[0] for col in cursor.description]
    cursor.close()

    # Create a namedtuple based on the column names and return the data
    MangaRows = namedtuple("MangaRow", columns)
    all_manga = [MangaRows(*row) for row in rows]
    
    # Render a template to show all manga
    return render_template('all_manga.html', manga_list=all_manga, columns=columns)

if __name__ == '__main__':
    app.run(debug=True)