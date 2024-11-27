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

#TODO:
#- Add filtering to the table in all_manga.html (javascript)
#- Add skin to manga.html and index.html (pure css or bootstrap?)
#- Cleanup backend python
#- 

def get_image_url(manga_id):
    # API URL to get the chapter details (images)
    url = f"https://api.mangadex.org/manga/{manga_id}"

    # Fetch the data from the MangaDex API
    response = requests.get(url)
    manga_data = response.json()

    for relationship in manga_data['data']['relationships']:
        if relationship['type'] == 'cover_art':
            cover_art_id = relationship['id']
            break
    
    if cover_art_id:
        cover_url = f"https://api.mangadex.org/cover/{cover_art_id}"
        response = requests.get(cover_url)
        cover_response = response.json()
        file_name = cover_response["data"]["attributes"]["fileName"]
        
        base_url = "https://uploads.mangadex.org/covers"
        full_image_url = f"{base_url}/{manga_id}/{file_name}.256.jpg"
    return full_image_url


    

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

    # Use a proxy URL for the image
    proxy_url = url_for('proxy_image', manga_id=manga.id_manga)
    
    # Render the manga page with the proxy URL
    return render_template('manga.html', manga=manga, image_url=proxy_url)


@app.route('/proxy-image/<manga_id>')
def proxy_image(manga_id):
    # Logic to fetch the image URL for the given manga ID
    full_image_url = get_image_url(manga_id)
    if not full_image_url:
        return "Image not found.", 404

    try:
        # Fetch the image from the URL
        response = requests.get(full_image_url, stream=True)
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
    return render_template('all_manga.html', manga_list=all_manga)

if __name__ == '__main__':
    app.run(debug=True)