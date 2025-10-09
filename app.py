from dotenv import load_dotenv
load_dotenv()  # Carga las variables del archivo .env

from flask import Flask, jsonify, request, send_from_directory, Response
import lxml.etree as ET  # Cambiado a lxml para permitir XSLT

# Inicializa la aplicación Flask
app = Flask(__name__, static_folder="static")

# -------------------------------------------------
#  RUTAS PARA SERVIR ARCHIVOS XML, XSL Y CSS
# -------------------------------------------------

# Servir archivos XML (desde /data)
@app.route('/data/<path:filename>')
def data_files(filename):
    return send_from_directory('data', filename)

# Servir archivos XSL (desde /frontend)
@app.route('/frontend/<path:filename>')
def frontend_files(filename):
    return send_from_directory('frontend', filename)

# -------------------------------------------------
#  RUTA PRINCIPAL (usa XML + XSL para renderizar)
# -------------------------------------------------
@app.route('/')
def index():
    # Cargar el XML y el XSL
    xml = ET.parse('data/spotify.xml')
    xsl = ET.parse('frontend/spotify.xsl')

    # Aplicar la transformación XSLT
    transform = ET.XSLT(xsl)
    html_result = transform(xml)

    # Devolver el HTML generado
    return Response(str(html_result), mimetype='text/html')


# -------------------------------------------------
#  FUNCIONES Y RUTAS DE API
# -------------------------------------------------

def obtener_datos_spotify():
    """Lee el XML y devuelve una lista de canciones."""
    tree = ET.parse('data/spotify.xml')
    root = tree.getroot()

    artistas = {a.get('id'): a.find('nombre').text for a in root.findall('.//artista')}
    albumes = {al.get('id'): (al.find('titulo').text, al.get('artista_id')) for al in root.findall('.//album')}

    lista_canciones = []
    for c in root.findall('.//cancion'):
        album_id = c.get('album_id')
        album_titulo, artista_id = albumes.get(album_id, ("Desconocido", "N/A"))
        artista_nombre = artistas.get(artista_id, "Desconocido")
        lista_canciones.append({
            "id": cancion_node.get('id'),
            "titulo": c.find('titulo').text,
            "artista": artista_nombre,
            "album": album_titulo,
            "genero": c.find('genero').text,
            "duracion": c.find('duracion').text
        })
    return lista_canciones


@app.route('/api/canciones')
def get_canciones():
    canciones = obtener_datos_spotify()
    return jsonify(canciones)


@app.route('/api/canciones', methods=['POST'])
def add_cancion():
    datos = request.get_json()
    nombre_artista_nuevo = datos['artista']
    titulo_album_nuevo = datos['album']

    tree = ET.parse('data/spotify.xml')
    root = tree.getroot()

    # --- Artista ---
    artista_id = None
    artistas_root = root.find('artistas')
    for artista in artistas_root.findall('artista'):
        if artista.find('nombre').text.lower() == nombre_artista_nuevo.lower():
            artista_id = artista.get('id')
            break
    if artista_id is None:
        nuevo_id_artista = "ART" + str(len(artistas_root.findall('artista')) + 1).zfill(2)
        elemento_artista = ET.Element('artista', attrib={'id': nuevo_id_artista})
        nombre = ET.SubElement(elemento_artista, 'nombre')
        nombre.text = nombre_artista_nuevo
        artistas_root.append(elemento_artista)
        artista_id = nuevo_id_artista

    # --- Álbum ---
    album_id = None
    albumes_root = root.find('albumes')
    for album in albumes_root.findall('album'):
        if album.find('titulo').text.lower() == titulo_album_nuevo.lower():
            album_id = album.get('id')
            break
    if album_id is None:
        nuevo_id_album = "ALB" + str(len(albumes_root.findall('album')) + 1).zfill(2)
        elemento_album = ET.Element('album', attrib={'id': nuevo_id_album, 'artista_id': artista_id})
        titulo = ET.SubElement(elemento_album, 'titulo')
        titulo.text = titulo_album_nuevo
        albumes_root.append(elemento_album)
        album_id = nuevo_id_album

    # --- Canción ---
    canciones_root = root.find('canciones')
    nuevo_id_cancion = "C" + str(len(canciones_root.findall('cancion')) + 1).zfill(3)

    elemento_cancion = ET.Element('cancion', attrib={'id': nuevo_id_cancion, 'album_id': album_id})
    ET.SubElement(elemento_cancion, 'titulo').text = datos['titulo']
    ET.SubElement(elemento_cancion, 'genero').text = datos['genero']
    ET.SubElement(elemento_cancion, 'duracion').text = datos['duracion']
    canciones_root.append(elemento_cancion)

    tree.write('data/spotify.xml', encoding='utf-8', xml_declaration=True)

    return jsonify({"mensaje": "Canción añadida con éxito", "id": nuevo_id_cancion}), 201
# Esto permite ejecutar el servidor con el comando 'flask run'
if __name__ == '__main__':
    app.run(debug=True)
