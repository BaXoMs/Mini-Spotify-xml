from flask import Flask, jsonify, request, send_from_directory
from owlready2 import *
import os

app = Flask(__name__)

# --- CONFIGURACIÓN ---
ONTOLOGY_PATH = os.path.join("data", "Spotify.rdf")
BASE_IRI = "http://www.semanticweb.org/asus/ontologies/2025/10/untitled-ontology-15#"

try:
    onto = get_ontology(ONTOLOGY_PATH).load()
    print(f"✅ ÉXITO: Ontología cargada desde {ONTOLOGY_PATH}")
except Exception as e:
    print(f"❌ ERROR: No se pudo cargar la ontología. {e}")

def save_ontology():
    try:
        onto.save(file=ONTOLOGY_PATH, format="rdfxml")
        print("💾 Ontología guardada.")
    except Exception as e:
        print(f"Error al guardar: {e}")

def get_safe_property(individual, prop_name):
    val = getattr(individual, prop_name)
    return val[0] if val else ""

def get_related_name(individual, prop_name, name_prop):
    relations = getattr(individual, prop_name)
    if not relations: return "Desconocido"
    related_obj = relations[0]
    name_val = getattr(related_obj, name_prop)
    return name_val[0] if name_val else str(related_obj.name)

# --- RECOLECTOR DE BASURA (NUEVO) ---
def limpiar_huerfanos(posible_artista, posible_album, posible_genero):
    """
    Verifica si las entidades se quedaron sin canciones.
    Si están vacías, las elimina del archivo RDF.
    """
    print("🧹 Ejecutando recolección de basura...")
    
    # 1. Limpiar Álbum si no tiene canciones
    if posible_album:
        canciones_en_album = onto.search(type=onto.Cancion, perteneceAAlbum=posible_album)
        # Si la lista está vacía (o la canción actual ya fue desvinculada), borramos
        if not canciones_en_album:
            print(f"   -> Borrando álbum huérfano: {posible_album.name}")
            destroy_entity(posible_album)

    # 2. Limpiar Artista si no tiene canciones vinculadas (vía artista principal)
    if posible_artista:
        canciones_de_artista = onto.search(type=onto.Cancion, tieneArtistaPrincipal=posible_artista)
        # También podríamos revisar si tiene álbumes, pero simplificamos:
        if not canciones_de_artista:
            print(f"   -> Borrando artista huérfano: {posible_artista.name}")
            destroy_entity(posible_artista)

    # 3. Limpiar Género
    if posible_genero:
        canciones_genero = onto.search(type=onto.Cancion, tieneGenero=posible_genero)
        if not canciones_genero:
            print(f"   -> Borrando género huérfano: {posible_genero.name}")
            destroy_entity(posible_genero)

# --- RUTAS ---
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# --- API CRUD ---

@app.route('/api/canciones', methods=['GET'])
def get_canciones():
    query = request.args.get('q', '').lower()
    canciones_list = []
    
    for cancion in onto.Cancion.instances():
        titulo = get_safe_property(cancion, "tieneTituloCancion")
        artista = get_related_name(cancion, "tieneArtistaPrincipal", "tieneNombre")
        album = get_related_name(cancion, "perteneceAAlbum", "tieneTituloAlbum")
        genero = get_related_name(cancion, "tieneGenero", "tieneNombre")
        duracion = get_safe_property(cancion, "tieneDuracion")

        if query and (query not in titulo.lower() and query not in artista.lower()):
            continue

        canciones_list.append({
            "id": cancion.name,
            "titulo": titulo,
            "artista": artista,
            "album": album,
            "genero": genero,
            "duracion": str(duracion)
        })
    return jsonify(canciones_list)

@app.route('/api/canciones', methods=['POST'])
def add_cancion():
    print("🔵 AGREGAR canción...")
    data = request.json
    song_id = data['titulo'].replace(" ", "_")
    
    # 1. Gestión de Entidades
    artist_id = data['artista'].replace(" ", "_")
    artista = onto.search_one(iri=f"*{artist_id}")
    if not artista:
        artista = onto.Artista(artist_id)
        artista.tieneNombre = [data['artista']]

    genre_id = data['genero'].replace(" ", "_")
    genero = onto.search_one(iri=f"*{genre_id}")
    if not genero:
        genero = onto.Genero(genre_id)
        genero.tieneNombre = [data['genero']]

    album_id = data['album'].replace(" ", "_")
    album = onto.search_one(iri=f"*{album_id}")
    if not album:
        album = onto.Album(album_id)
        album.tieneTituloAlbum = [data['album']]
        album.tieneArtistaPrincipal = [artista]
        album.tieneGenero = [genero]

    # 2. Crear Canción
    nueva_cancion = onto.search_one(iri=f"*{song_id}")
    if not nueva_cancion:
        nueva_cancion = onto.Cancion(song_id)
    
    nueva_cancion.tieneTituloCancion = [data['titulo']]
    try: nueva_cancion.tieneDuracion = [int(data['duracion'])]
    except: nueva_cancion.tieneDuracion = [0]

    nueva_cancion.tieneArtistaPrincipal = [artista]
    nueva_cancion.perteneceAAlbum = [album]
    nueva_cancion.tieneGenero = [genero]
    
    save_ontology()
    return jsonify({"status": "success", "id": song_id})

@app.route('/api/canciones/<song_id>', methods=['PUT'])
def update_cancion(song_id):
    print(f"🟠 EDITAR canción ID: {song_id}")
    data = request.json
    cancion = onto.search_one(iri=f"*{song_id}")
    
    if not cancion:
        return jsonify({"error": "Canción no encontrada"}), 404

    try:
        # 1. Guardar referencias a los objetos VIEJOS antes de cambiarlos
        old_artist = cancion.tieneArtistaPrincipal[0] if cancion.tieneArtistaPrincipal else None
        old_album = cancion.perteneceAAlbum[0] if cancion.perteneceAAlbum else None
        old_genre = cancion.tieneGenero[0] if cancion.tieneGenero else None

        # 2. Actualizar Textos
        cancion.tieneTituloCancion = [data['titulo']]
        try: cancion.tieneDuracion = [int(data['duracion'])]
        except: pass
        
        # 3. Buscar o Crear los NUEVOS
        # Artista
        artist_id = data['artista'].replace(" ", "_")
        nuevo_artista = onto.search_one(iri=f"*{artist_id}")
        if not nuevo_artista:
            nuevo_artista = onto.Artista(artist_id)
            nuevo_artista.tieneNombre = [data['artista']]
        cancion.tieneArtistaPrincipal = [nuevo_artista]

        # Género
        genre_id = data['genero'].replace(" ", "_")
        nuevo_genero = onto.search_one(iri=f"*{genre_id}")
        if not nuevo_genero:
            nuevo_genero = onto.Genero(genre_id)
            nuevo_genero.tieneNombre = [data['genero']]
        cancion.tieneGenero = [nuevo_genero]

        # Álbum
        album_id = data['album'].replace(" ", "_")
        nuevo_album = onto.search_one(iri=f"*{album_id}")
        if not nuevo_album:
            nuevo_album = onto.Album(album_id)
            nuevo_album.tieneTituloAlbum = [data['album']]
            nuevo_album.tieneArtistaPrincipal = [nuevo_artista]
            nuevo_album.tieneGenero = [nuevo_genero]
        cancion.perteneceAAlbum = [nuevo_album]
        
        # 4. LIMPIEZA: Verificar si los viejos se quedaron huérfanos
        # Solo limpiamos si son diferentes a los nuevos
        if old_artist != nuevo_artista:
            limpiar_huerfanos(old_artist, None, None)
        if old_album != nuevo_album:
            limpiar_huerfanos(None, old_album, None)
        if old_genre != nuevo_genero:
            limpiar_huerfanos(None, None, old_genre)

        save_ontology()
        return jsonify({"status": "updated"})

    except Exception as e:
        print(f"❌ ERROR UPDATE: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/canciones/<song_id>', methods=['DELETE'])
def delete_cancion(song_id):
    cancion = onto.search_one(iri=f"*{song_id}")
    
    if cancion:
        print(f"🔴 Eliminando canción: {song_id}")
        # 1. Guardar referencias para ver si limpiamos después
        old_artist = cancion.tieneArtistaPrincipal[0] if cancion.tieneArtistaPrincipal else None
        old_album = cancion.perteneceAAlbum[0] if cancion.perteneceAAlbum else None
        old_genre = cancion.tieneGenero[0] if cancion.tieneGenero else None

        # 2. Destruir la canción
        destroy_entity(cancion)
        
        # 3. Limpiar papás huérfanos
        limpiar_huerfanos(old_artist, old_album, old_genre)

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

if __name__ == '__main__':
    app.run(debug=True)