import xml.etree.ElementTree as ET
from flask import Flask, jsonify, render_template

# Inicializa la aplicación Flask
app = Flask(__name__)

# Función para leer y procesar el XML
def obtener_datos_spotify():
    tree = ET.parse('data/spotify.xml')
    root = tree.getroot()

    # Usamos diccionarios para buscar nombres de forma eficiente
    artistas = {artista.get('id'): artista.find('nombre').text for artista in root.findall('.//artista')}
    albumes = {album.get('id'): (album.find('titulo').text, album.get('artista_id')) for album in root.findall('.//album')}

    # Creamos una lista de diccionarios con la información de cada canción
    lista_canciones = []
    for cancion_node in root.findall('.//cancion'):
        album_id = cancion_node.get('album_id')
        album_titulo, artista_id = albumes.get(album_id, ("Desconocido", "N/A"))
        artista_nombre = artistas.get(artista_id, "Desconocido")
        
        cancion_info = {
            "titulo": cancion_node.find('titulo').text,
            "artista": artista_nombre,
            "album": album_titulo,
            "genero": cancion_node.find('genero').text,
            "duracion": cancion_node.find('duracion').text
        }
        lista_canciones.append(cancion_info)
    
    return lista_canciones

# Ruta principal que muestra la página web (el frontend)
@app.route('/')
def index():
    return render_template('index.html')

# Ruta de la API que devuelve los datos de las canciones en formato JSON
@app.route('/api/canciones')
def get_canciones():
    canciones = obtener_datos_spotify()
    return jsonify(canciones)

# Esto permite ejecutar el servidor con el comando 'flask run'
if __name__ == '__main__':
    app.run(debug=True)