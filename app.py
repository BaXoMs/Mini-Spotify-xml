from flask import Flask, jsonify, request, send_from_directory
from owlready2 import *
import os

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# 1. CORRECCIÓN DE RUTA: Apunta exactamente a 'Spotify.rdf' (respetando mayúsculas)
ONTOLOGY_PATH = os.path.join("data", "Spotify.rdf")

# Definimos el namespace base (Copiado de tu archivo original)
BASE_IRI = "http://www.semanticweb.org/asus/ontologies/2025/10/untitled-ontology-15#"

# Cargamos la ontología con manejo de errores
try:
    onto = get_ontology(ONTOLOGY_PATH).load()
    print(f"✅ ÉXITO: Ontología cargada desde {ONTOLOGY_PATH}")
except Exception as e:
    print(f"❌ ERROR CRÍTICO: No se pudo cargar la ontología.")
    print(f"Detalle del error: {e}")
    print(f"Verifica que el archivo 'Spotify.rdf' esté en la carpeta 'data'.")

def save_ontology():
    """Guarda los cambios en el archivo RDF"""
    try:
        onto.save(file=ONTOLOGY_PATH, format="rdfxml")
        print("💾 Ontología guardada correctamente.")
    except Exception as e:
        print(f"Error al guardar: {e}")

def get_safe_property(individual, prop_name):
    """Obtiene el valor de una DataProperty (Texto/Número) de forma segura"""
    val = getattr(individual, prop_name)
    if not val: 
        return "" 
    return val[0] # Owlready devuelve listas, tomamos el primero

def get_related_name(individual, prop_name, name_prop):
    """
    Obtiene el nombre de un objeto relacionado (ObjectProperty).
    Sirve para obtener el nombre real de: Artista, Album y Género.
    """
    relations = getattr(individual, prop_name)
    if not relations:
        return "Desconocido"
    
    related_obj = relations[0] # Tomamos el primer objeto relacionado
    
    # Buscamos la propiedad de nombre dentro de ese objeto (ej. tieneNombre)
    name_val = getattr(related_obj, name_prop)
    
    # Si tiene nombre, lo devolvemos. Si no, devolvemos el ID del objeto.
    return name_val[0] if name_val else str(related_obj.name)

# --- RUTAS DE LA APLICACIÓN ---

@app.route('/')
def index():
    # CAMBIO: Ahora enviamos index.html
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# --- API CRUD SEMÁNTICO (OWL) ---

@app.route('/api/canciones', methods=['GET'])
def get_canciones():
    query = request.args.get('q', '').lower()
    canciones_list = []

    # Iteramos sobre todas las instancias de la clase Cancion
    for cancion in onto.Cancion.instances():
        
        # 1. Obtener datos directos (Strings/Ints)
        titulo = get_safe_property(cancion, "tieneTituloCancion")
        duracion = get_safe_property(cancion, "tieneDuracion")
        
        # 2. Obtener relaciones (Objetos conectados)
        # Aquí solucionamos lo del Género, Artista y Album buscando sus nombres
        artista = get_related_name(cancion, "tieneArtistaPrincipal", "tieneNombre")
        album = get_related_name(cancion, "perteneceAAlbum", "tieneTituloAlbum")
        genero = get_related_name(cancion, "tieneGenero", "tieneNombre")

        # Filtro de búsqueda
        if query and (query not in titulo.lower() and query not in artista.lower()):
            continue

        canciones_list.append({
            "id": cancion.name, # El ID es el nombre del recurso
            "titulo": titulo,
            "artista": artista,
            "album": album,
            "genero": genero, # Devuelve el nombre (ej. "Reggaeton") no la URL
            "duracion": str(duracion)
        })

    return jsonify(canciones_list)

@app.route('/api/canciones', methods=['POST'])
def add_cancion():
    data = request.json
    
    # Creamos IDs válidos reemplazando espacios por guiones bajos
    song_id = data['titulo'].replace(" ", "_")
    artist_id = data['artista'].replace(" ", "_")
    album_id = data['album'].replace(" ", "_")
    genre_id = data['genero'].replace(" ", "_")

    # 1. GESTIÓN DE ARTISTA (Buscar o Crear)
    artista = onto.search_one(iri=f"*{artist_id}")
    if not artista:
        artista = onto.Artista(artist_id)
        artista.tieneNombre = [data['artista']]

    # 2. GESTIÓN DE GÉNERO (Buscar o Crear) - CORRECCIÓN SOLICITADA
    genero = onto.search_one(iri=f"*{genre_id}")
    if not genero:
        genero = onto.Genero(genre_id)
        genero.tieneNombre = [data['genero']]

    # 3. GESTIÓN DE ÁLBUM (Buscar o Crear)
    album = onto.search_one(iri=f"*{album_id}")
    if not album:
        album = onto.Album(album_id)
        album.tieneTituloAlbum = [data['album']]
        album.tieneArtistaPrincipal = [artista] # Conexión Album -> Artista
        album.tieneGenero = [genero]            # Conexión Album -> Genero

    # 4. CREAR CANCIÓN
    nueva_cancion = onto.search_one(iri=f"*{song_id}")
    if not nueva_cancion:
        nueva_cancion = onto.Cancion(song_id)
    
    # Asignar Propiedades de Datos
    nueva_cancion.tieneTituloCancion = [data['titulo']]
    try:
        nueva_cancion.tieneDuracion = [int(data['duracion'])] # Convertimos a entero
    except:
        nueva_cancion.tieneDuracion = [0]

    # Asignar Relaciones (Conectamos los objetos)
    nueva_cancion.tieneArtistaPrincipal = [artista]
    nueva_cancion.perteneceAAlbum = [album]
    nueva_cancion.tieneGenero = [genero]
    
    save_ontology()
    return jsonify({"status": "success", "id": song_id})

@app.route('/api/canciones/<song_id>', methods=['DELETE'])
def delete_cancion(song_id):
    cancion = onto.search_one(iri=f"*{song_id}")
    if cancion:
        destroy_entity(cancion)
        save_ontology()
        return jsonify({"status": "deleted"})
    return jsonify({"error": "No encontrada"}), 404

@app.route('/api/canciones/<song_id>', methods=['GET'])
def get_one_cancion(song_id):
    cancion = onto.search_one(iri=f"*{song_id}")
    if cancion:
        return jsonify({
            "id": cancion.name,
            "titulo": get_safe_property(cancion, "tieneTituloCancion"),
            "artista": get_related_name(cancion, "tieneArtistaPrincipal", "tieneNombre"),
            "album": get_related_name(cancion, "perteneceAAlbum", "tieneTituloAlbum"),
            "genero": get_related_name(cancion, "tieneGenero", "tieneNombre"),
            "duracion": get_safe_property(cancion, "tieneDuracion")
        })
    return jsonify({"error": "Not found"}), 404

@app.route('/api/canciones/<song_id>', methods=['PUT'])
def update_cancion(song_id):
    data = request.json
    cancion = onto.search_one(iri=f"*{song_id}")
    
    if cancion:
        # Actualizamos propiedades simples
        cancion.tieneTituloCancion = [data['titulo']]
        try:
            cancion.tieneDuracion = [int(data['duracion'])]
        except:
            pass
        
        # NOTA: Para un proyecto completo, aquí deberías actualizar también
        # las relaciones (artista, album, genero) si cambiaron.
        
        save_ontology()
        return jsonify({"status": "updated"})
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)