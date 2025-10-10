# app.py - Versión Final Híbrida

# --- Importaciones ---
from dotenv import load_dotenv
from lxml import etree
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, request

# --- Configuración Inicial ---
load_dotenv()  # Carga las variables del archivo .env
app = Flask(__name__) # Inicializa la aplicación Flask

# --- Lógica de Datos ---
def obtener_datos_spotify():
    """Lee el archivo XML y lo convierte en una lista de diccionarios para la API."""
    tree = ET.parse('data/spotify.xml')
    root = tree.getroot()
    artistas = {artista.get('id'): artista.find('nombre').text for artista in root.findall('.//artista')}
    albumes = {album.get('id'): (album.find('titulo').text, album.get('artista_id')) for album in root.findall('.//album')}
    
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

# --- Ruta Principal (Renderizado con XSLT) ---
@app.route('/')
def index():
    """Renderiza la vista principal aplicando la transformación XSLT en el servidor."""
    try:
        xml_doc = etree.parse("data/spotify.xml")
        xsl_doc = etree.parse("spotify.xsl")
        transform = etree.XSLT(xsl_doc)
        result_tree = transform(xml_doc)
        return str(result_tree)
    except Exception as e:
        return f"Ocurrió un error en la transformación XSLT: {e}", 500

# --- API Endpoints (Para la interactividad con JavaScript) ---

@app.route('/api/canciones', methods=['GET'])
def get_canciones():
    """Devuelve todas las canciones o las filtra según un parámetro de búsqueda 'q'."""
    query = request.args.get('q', '').lower()
    todas_las_canciones = obtener_datos_spotify()
    if not query:
        return jsonify(todas_las_canciones)
    canciones_filtradas = [
        c for c in todas_las_canciones if 
        query in c['titulo'].lower() or 
        query in c['artista'].lower() or 
        query in c['album'].lower()
    ]
    return jsonify(canciones_filtradas)

@app.route('/api/canciones/<string:cancion_id>', methods=['GET'])
def get_cancion(cancion_id):
    """Devuelve los datos de una única canción por su ID."""
    cancion_encontrada = next((c for c in obtener_datos_spotify() if c['id'] == cancion_id), None)
    if cancion_encontrada:
        return jsonify(cancion_encontrada)
    return jsonify({"error": "Canción no encontrada"}), 404

@app.route('/api/canciones', methods=['POST'])
def add_cancion():
    """Añade una nueva canción, creando el artista y/o álbum si no existen."""
    datos = request.get_json()
    tree = ET.parse('data/spotify.xml')
    root = tree.getroot()
    
    # Lógica para Artista (buscar o crear)
    nombre_artista_nuevo = datos['artista']
    artista_id = None
    artistas_root = root.find('artistas')
    for artista in artistas_root.findall('artista'):
        if artista.find('nombre').text.lower() == nombre_artista_nuevo.lower():
            artista_id = artista.get('id')
            break
    if artista_id is None:
        nuevo_id_artista = "ART" + str(len(artistas_root.findall('artista')) + 1).zfill(2)
        elemento_artista = ET.Element('artista', attrib={'id': nuevo_id_artista})
        ET.SubElement(elemento_artista, 'nombre').text = nombre_artista_nuevo
        artistas_root.append(elemento_artista)
        artista_id = nuevo_id_artista

    # Lógica para Álbum (buscar o crear)
    titulo_album_nuevo = datos['album']
    album_id = None
    albumes_root = root.find('albumes')
    for album in albumes_root.findall('album'):
        if album.find('titulo').text.lower() == titulo_album_nuevo.lower():
            album_id = album.get('id')
            break
    if album_id is None:
        nuevo_id_album = "ALB" + str(len(albumes_root.findall('album')) + 1).zfill(2)
        elemento_album = ET.Element('album', attrib={'id': nuevo_id_album, 'artista_id': artista_id})
        ET.SubElement(elemento_album, 'titulo').text = titulo_album_nuevo
        albumes_root.append(elemento_album)
        album_id = nuevo_id_album
    
    # Crear la nueva canción
    canciones_root = root.find('canciones')
    nuevo_id_cancion = "C" + str(len(canciones_root.findall('cancion')) + 1).zfill(3)
    elemento_cancion = ET.Element('cancion', attrib={'id': nuevo_id_cancion, 'album_id': album_id})
    ET.SubElement(elemento_cancion, 'titulo').text = datos['titulo']
    ET.SubElement(elemento_cancion, 'genero').text = datos['genero']
    ET.SubElement(elemento_cancion, 'duracion').text = datos['duracion']
    canciones_root.append(elemento_cancion)

    tree.write('data/spotify.xml', encoding='utf-8', xml_declaration=True)
    return jsonify({"mensaje": "Canción añadida con éxito", "id": nuevo_id_cancion}), 201

# --- Pega esta función en app.py, reemplazando la versión incorrecta ---

@app.route('/api/canciones/<string:cancion_id>', methods=['PUT'])
def update_cancion(cancion_id):
    """Actualiza una canción existente, incluyendo su artista y álbum."""
    try:
        datos_actualizados = request.get_json()
        tree = ET.parse('data/spotify.xml')
        root = tree.getroot()
        
        cancion_a_actualizar = root.find(f".//cancion[@id='{cancion_id}']")
        
        if cancion_a_actualizar is not None:
            # --- Lógica para Artista y Álbum (la versión completa) ---
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
                ET.SubElement(elemento_artista, 'nombre').text = nombre_artista_nuevo
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
                ET.SubElement(elemento_album, 'titulo').text = titulo_album_nuevo
                albumes_root.append(elemento_album)
                album_id = nuevo_id_album

            # --- Actualización de la canción ---
            cancion_a_actualizar.find('titulo').text = datos_actualizados['titulo']
            cancion_a_actualizar.find('genero').text = datos_actualizados['genero']
            cancion_a_actualizar.find('duracion').text = datos_actualizados['duracion']
            
            # ¡Actualizamos la referencia al álbum!
            cancion_a_actualizar.set('album_id', album_id)
            
            tree.write('data/spotify.xml', encoding='utf-8', xml_declaration=True)
            return jsonify({"mensaje": f"Canción {cancion_id} actualizada con éxito"}), 200
        else:
            return jsonify({"error": "Canción no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/canciones/<string:cancion_id>', methods=['DELETE'])
def delete_cancion(cancion_id):
    """Elimina una canción y limpia los álbumes/artistas huérfanos."""
    try:
        tree = ET.parse('data/spotify.xml')
        root = tree.getroot()

        # 1. Encontrar y eliminar la canción
        canciones_root = root.find('canciones')
        cancion_a_eliminar = canciones_root.find(f".//cancion[@id='{cancion_id}']")

        if cancion_a_eliminar is not None:
            # Guardamos los IDs antes de borrar la canción
            album_id_borrado = cancion_a_eliminar.get('album_id')
            
            # Eliminamos la canción
            canciones_root.remove(cancion_a_eliminar)

            # 2. Comprobar si el álbum quedó huérfano
            otras_canciones_en_album = canciones_root.find(f".//cancion[@album_id='{album_id_borrado}']")
            if otras_canciones_en_album is None:
                # Si no hay más canciones en ese álbum, lo eliminamos
                albumes_root = root.find('albumes')
                album_a_eliminar = albumes_root.find(f".//album[@id='{album_id_borrado}']")
                if album_a_eliminar is not None:
                    artista_id_borrado = album_a_eliminar.get('artista_id')
                    albumes_root.remove(album_a_eliminar)
                    
                    # 3. Comprobar si el artista quedó huérfano
                    otros_albumes_del_artista = albumes_root.find(f".//album[@artista_id='{artista_id_borrado}']")
                    if otros_albumes_del_artista is None:
                        # Si no hay más álbumes de ese artista, lo eliminamos
                        artistas_root = root.find('artistas')
                        artista_a_eliminar = artistas_root.find(f".//artista[@id='{artista_id_borrado}']")
                        if artista_a_eliminar is not None:
                            artistas_root.remove(artista_a_eliminar)

            # 4. Guardar todos los cambios en el archivo
            tree.write('data/spotify.xml', encoding='utf-8', xml_declaration=True)
            return jsonify({"mensaje": f"Canción {cancion_id} y datos huérfanos eliminados"}), 200
        else:
            return jsonify({"error": "Canción no encontrada"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# --- Ejecución de la Aplicación ---
if __name__ == '__main__':
    app.run(debug=True)