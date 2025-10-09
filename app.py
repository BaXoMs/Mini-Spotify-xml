from dotenv import load_dotenv

load_dotenv() # Carga las variables del archivo .env

# ... el resto de tu código
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, render_template, request

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
            "id": cancion_node.get('id'),
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
@app.route('/api/canciones', methods=['POST'])
def add_cancion():
    # 1. Recibir los datos completos del frontend
    datos = request.get_json()
    nombre_artista_nuevo = datos['artista']
    titulo_album_nuevo = datos['album']

    # 2. Cargar el árbol XML existente
    tree = ET.parse('data/spotify.xml')
    root = tree.getroot()

    # --- Lógica para Artista ---
    artista_id = None
    artistas_root = root.find('artistas')
    # Buscar si el artista ya existe
    for artista in artistas_root.findall('artista'):
        if artista.find('nombre').text.lower() == nombre_artista_nuevo.lower():
            artista_id = artista.get('id')
            break
    # Si no existe, crearlo
    if artista_id is None:
        nuevo_id_artista = "ART" + str(len(artistas_root.findall('artista')) + 1).zfill(2)
        elemento_artista = ET.Element('artista', attrib={'id': nuevo_id_artista})
        nombre = ET.SubElement(elemento_artista, 'nombre')
        nombre.text = nombre_artista_nuevo
        # Aquí podríamos añadir un campo 'pais' si quisiéramos
        artistas_root.append(elemento_artista)
        artista_id = nuevo_id_artista

    # --- Lógica para Álbum ---
    album_id = None
    albumes_root = root.find('albumes')
    # Buscar si el álbum ya existe
    for album in albumes_root.findall('album'):
        if album.find('titulo').text.lower() == titulo_album_nuevo.lower():
            album_id = album.get('id')
            break
    # Si no existe, crearlo
    if album_id is None:
        nuevo_id_album = "ALB" + str(len(albumes_root.findall('album')) + 1).zfill(2)
        elemento_album = ET.Element('album', attrib={'id': nuevo_id_album, 'artista_id': artista_id})
        titulo = ET.SubElement(elemento_album, 'titulo')
        titulo.text = titulo_album_nuevo
        # Aquí podríamos añadir 'anio'
        albumes_root.append(elemento_album)
        album_id = nuevo_id_album
    
    # --- Lógica para Canción (como antes, pero con los IDs correctos) ---
    canciones_root = root.find('canciones')
    nuevo_id_cancion = "C" + str(len(canciones_root.findall('cancion')) + 1).zfill(3)
    
    elemento_cancion = ET.Element('cancion', attrib={'id': nuevo_id_cancion, 'album_id': album_id})
    
    titulo = ET.SubElement(elemento_cancion, 'titulo')
    titulo.text = datos['titulo']
    
    genero = ET.SubElement(elemento_cancion, 'genero')
    genero.text = datos['genero']
    
    duracion = ET.SubElement(elemento_cancion, 'duracion')
    duracion.text = datos['duracion']
    
    canciones_root.append(elemento_cancion)

    # 4. Guardar los cambios en el archivo XML
    tree.write('data/spotify.xml', encoding='utf-8', xml_declaration=True)

    # 5. Devolver una respuesta de éxito
    return jsonify({"mensaje": "Canción añadida con éxito", "id": nuevo_id_cancion}), 201
# Esto permite ejecutar el servidor con el comando 'flask run'
@app.route('/api/canciones/<string:cancion_id>', methods=['DELETE'])
def delete_cancion(cancion_id):
    try:
        # 1. Cargar el árbol XML
        tree = ET.parse('data/spotify.xml')
        root = tree.getroot()

        # 2. Encontrar la canción a eliminar
        canciones_root = root.find('canciones')
        cancion_a_eliminar = canciones_root.find(f".//cancion[@id='{cancion_id}']")

        # 3. Si la canción existe, eliminarla
        if cancion_a_eliminar is not None:
            canciones_root.remove(cancion_a_eliminar)
            # 4. Guardar los cambios en el archivo
            tree.write('data/spotify.xml', encoding='utf-8', xml_declaration=True)
            return jsonify({"mensaje": f"Canción con id {cancion_id} eliminada"}), 200
        else:
            return jsonify({"error": "Canción no encontrada"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Ruta para OBTENER una sola canción por su ID
@app.route('/api/canciones/<string:cancion_id>', methods=['GET'])
def get_cancion(cancion_id):
    try:
        datos = obtener_datos_spotify()
        # Busca la canción con el ID correspondiente en la lista
        cancion_encontrada = next((c for c in datos if c['id'] == cancion_id), None)
        
        if cancion_encontrada:
            return jsonify(cancion_encontrada), 200
        else:
            return jsonify({"error": "Canción no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para ACTUALIZAR una canción por su ID (VERSIÓN MEJORADA)
@app.route('/api/canciones/<string:cancion_id>', methods=['PUT'])
def update_cancion(cancion_id):
    try:
        datos_actualizados = request.get_json()
        tree = ET.parse('data/spotify.xml')
        root = tree.getroot()
        
        cancion_a_actualizar = root.find(f".//cancion[@id='{cancion_id}']")
        
        if cancion_a_actualizar is not None:
            # --- Lógica para Artista y Álbum (similar a la de 'add_cancion') ---
            nombre_artista_nuevo = datos_actualizados['artista']
            titulo_album_nuevo = datos_actualizados['album']
            
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

            # --- Actualización de la canción ---
            # Se actualizan los datos directos
            cancion_a_actualizar.find('titulo').text = datos_actualizados['titulo']
            cancion_a_actualizar.find('genero').text = datos_actualizados['genero']
            cancion_a_actualizar.find('duracion').text = datos_actualizados['duracion']
            
            # ¡Y lo más importante, se actualiza la referencia al álbum!
            cancion_a_actualizar.set('album_id', album_id)
            
            tree.write('data/spotify.xml', encoding='utf-8', xml_declaration=True)
            return jsonify({"mensaje": f"Canción {cancion_id} actualizada"}), 200
        else:
            return jsonify({"error": "Canción no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)