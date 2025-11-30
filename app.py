from flask import Flask, jsonify, request, send_from_directory
from owlready2 import *
import os

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# Ruta al archivo RDF generado en Protégé
ONTOLOGY_PATH = os.path.join("data", "Spotify.rdf")
BASE_IRI = "http://www.semanticweb.org/asus/ontologies/2025/10/untitled-ontology-15#"

# Carga inicial de la ontología
try:
    onto = get_ontology(ONTOLOGY_PATH).load()
    print(f"✅ ÉXITO: Ontología cargada desde {ONTOLOGY_PATH}")
except Exception as e:
    print(f"❌ ERROR: No se pudo cargar la ontología. {e}")

def save_ontology():
    """Guarda los cambios en el archivo RDF"""
    try:
        onto.save(file=ONTOLOGY_PATH, format="rdfxml")
        print("💾 Ontología guardada.")
    except Exception as e:
        print(f"Error al guardar: {e}")

def get_safe_property(individual, prop_name):
    """Obtiene datos de texto/número de forma segura"""
    val = getattr(individual, prop_name)
    return val[0] if val else ""

def get_related_name(individual, prop_name, name_prop):
    """Obtiene el nombre de un objeto relacionado"""
    relations = getattr(individual, prop_name)
    if not relations: return ""
    related_obj = relations[0]
    name_val = getattr(related_obj, name_prop)
    return name_val[0] if name_val else str(related_obj.name)

# --- RECOLECTOR DE BASURA (GARBAGE COLLECTOR) ---
def limpiar_huerfanos():
    """
    Elimina Artistas, Álbumes, Géneros y otras entidades que se quedaron sin uso.
    Mantiene la ontología limpia.
    """
    print("🧹 Ejecutando limpieza completa de huérfanos...")
    
    # 1. Limpiar Albumes vacíos
    for album in onto.Album.instances():
        if not onto.search(type=onto.Cancion, perteneceAAlbum=album):
            print(f"   -> Borrando álbum: {album.name}")
            destroy_entity(album)

    # 2. Limpiar Artistas vacíos
    for artista in onto.Artista.instances():
        if not onto.search(type=onto.Cancion, tieneArtistaPrincipal=artista):
            print(f"   -> Borrando artista: {artista.name}")
            destroy_entity(artista)
            
    # 3. Limpiar Generos vacíos
    for genero in onto.Genero.instances():
        # Check simple: si no lo usa ninguna canción ni álbum
        if not onto.search(type=onto.Cancion, tieneGenero=genero) and \
           not onto.search(type=onto.Album, tieneGenero=genero):
            print(f"   -> Borrando género: {genero.name}")
            destroy_entity(genero)

    # 4. Limpiar Nuevas Entidades (Compositor, Productor, Escritor, Discográfica)
    # Nota: Usamos los nombres de clases tal cual están en tu archivo OWL (ojo con mayúsculas/minúsculas)
    
    if hasattr(onto, 'Compositor'):
        for comp in onto.Compositor.instances():
            if not onto.search(type=onto.Cancion, tieneCompositor=comp):
                destroy_entity(comp)
            
    if hasattr(onto, 'productor'): # Nota: 'productor' en minúscula en tu owl
        for prod in onto.productor.instances(): 
            if not onto.search(type=onto.Cancion, tieneProductor=prod):
                destroy_entity(prod)

    if hasattr(onto, 'Escritor'):
        for esc in onto.Escritor.instances():
            if not onto.search(type=onto.Cancion, tieneEscritor=esc):
                destroy_entity(esc)
            
    if hasattr(onto, 'Dsicografia'): # Nota: 'Dsicografia' con error de dedo en tu owl original
        for disc in onto.Dsicografia.instances(): 
            if not onto.search(type=onto.Album, perteneceADiscografica=disc):
                destroy_entity(disc)

# --- HELPER DE CREACIÓN ---
def get_or_create(cls_name, name_value):
    """Busca una entidad por su nombre o crea una nueva si no existe"""
    if not name_value: return None
    clean_id = name_value.replace(" ", "_")
    
    # Accedemos dinámicamente a la clase en la ontología
    if not hasattr(onto, cls_name):
        print(f"⚠️ Advertencia: La clase {cls_name} no existe en la ontología.")
        return None

    ontology_class = getattr(onto, cls_name)
    instance = onto.search_one(iri=f"*{clean_id}")
    
    if not instance:
        instance = ontology_class(clean_id)
        # Asignamos la propiedad 'tieneNombre' si existe
        if hasattr(instance, 'tieneNombre'):
            instance.tieneNombre = [name_value]
    return instance

# --- RUTAS WEB ---
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# --- API CRUD SEMÁNTICO ---

@app.route('/api/canciones', methods=['GET'])
def get_canciones():
    query = request.args.get('q', '').lower()
    canciones_list = []
    
    for cancion in onto.Cancion.instances():
        titulo = get_safe_property(cancion, "tieneTituloCancion")
        artista = get_related_name(cancion, "tieneArtistaPrincipal", "tieneNombre")
        
        album_obj = cancion.perteneceAAlbum[0] if cancion.perteneceAAlbum else None
        album_nombre = album_obj.tieneTituloAlbum[0] if album_obj and album_obj.tieneTituloAlbum else "Desconocido"
        
        discografica = ""
        if album_obj and hasattr(album_obj, 'perteneceADiscografica') and album_obj.perteneceADiscografica:
            disc_obj = album_obj.perteneceADiscografica[0]
            discografica = disc_obj.tieneNombre[0] if disc_obj.tieneNombre else disc_obj.name

        compositor = get_related_name(cancion, "tieneCompositor", "tieneNombre")
        escritor = get_related_name(cancion, "tieneEscritor", "tieneNombre")
        productor = get_related_name(cancion, "tieneProductor", "tieneNombre")
        
        genero = get_related_name(cancion, "tieneGenero", "tieneNombre")
        duracion = get_safe_property(cancion, "tieneDuracion")

        # ============================
        # 🔍 FILTRO MEJORADO (solo esto cambiamos)
        # ============================
        if query:
            coincide = (
                query in titulo.lower() or
                query in artista.lower() or
                query in album_nombre.lower() or
                query in genero.lower()
            )
            if not coincide:
                continue

        canciones_list.append({
            "id": cancion.name,
            "titulo": titulo,
            "artista": artista,
            "album": album_nombre,
            "discografica": discografica,
            "genero": genero,
            "duracion": str(duracion),
            "compositor": compositor,
            "escritor": escritor,
            "productor": productor
        })
    return jsonify(canciones_list)

    query = request.args.get('q', '').lower()
    canciones_list = []
    
    for cancion in onto.Cancion.instances():
        titulo = get_safe_property(cancion, "tieneTituloCancion")
        artista = get_related_name(cancion, "tieneArtistaPrincipal", "tieneNombre")
        
        # Recuperamos la información extendida
        # Para Discografica, navegamos: Cancion -> Album -> Discografica
        album_obj = cancion.perteneceAAlbum[0] if cancion.perteneceAAlbum else None
        album_nombre = album_obj.tieneTituloAlbum[0] if album_obj and album_obj.tieneTituloAlbum else "Desconocido"
        
        discografica = ""
        if album_obj and hasattr(album_obj, 'perteneceADiscografica') and album_obj.perteneceADiscografica:
            disc_obj = album_obj.perteneceADiscografica[0]
            discografica = disc_obj.tieneNombre[0] if disc_obj.tieneNombre else disc_obj.name

        compositor = get_related_name(cancion, "tieneCompositor", "tieneNombre")
        escritor = get_related_name(cancion, "tieneEscritor", "tieneNombre")
        productor = get_related_name(cancion, "tieneProductor", "tieneNombre")
        
        genero = get_related_name(cancion, "tieneGenero", "tieneNombre")
        duracion = get_safe_property(cancion, "tieneDuracion")

        if query and (query not in titulo.lower() and query not in artista.lower()):
            continue

        canciones_list.append({
            "id": cancion.name,
            "titulo": titulo,
            "artista": artista,
            "album": album_nombre,
            "discografica": discografica,
            "genero": genero,
            "duracion": str(duracion),
            "compositor": compositor,
            "escritor": escritor,
            "productor": productor
        })
    return jsonify(canciones_list)

@app.route('/api/canciones', methods=['POST'])
def add_cancion():
    print("🔵 AGREGAR canción...")
    data = request.json
    song_id = data['titulo'].replace(" ", "_")
    
    # 1. Crear Entidades Principales
    artista = get_or_create("Artista", data['artista'])
    genero = get_or_create("Genero", data['genero'])
    
    # 2. Discográfica y Álbum
    # Usamos 'Dsicografia' tal cual aparece en tu archivo .owl (con el typo)
    discografica = get_or_create("Dsicografia", data.get('discografica')) 
    
    album = get_or_create("Album", data['album'])
    if album:
        album.tieneTituloAlbum = [data['album']]
        album.tieneArtistaPrincipal = [artista]
        album.tieneGenero = [genero]
        if discografica:
            album.perteneceADiscografica = [discografica]

    # 3. Entidades Secundarias
    compositor = get_or_create("Compositor", data.get('compositor'))
    escritor = get_or_create("Escritor", data.get('escritor'))
    productor = get_or_create("productor", data.get('productor')) # Minúscula en tu owl

    # 4. Crear Canción
    nueva_cancion = onto.search_one(iri=f"*{song_id}")
    if not nueva_cancion:
        nueva_cancion = onto.Cancion(song_id)
    
    nueva_cancion.tieneTituloCancion = [data['titulo']]
    try: nueva_cancion.tieneDuracion = [int(data['duracion'])]
    except: nueva_cancion.tieneDuracion = [0]

    # Asignar relaciones
    nueva_cancion.tieneArtistaPrincipal = [artista]
    nueva_cancion.perteneceAAlbum = [album]
    nueva_cancion.tieneGenero = [genero]
    
    if compositor: nueva_cancion.tieneCompositor = [compositor]
    if escritor: nueva_cancion.tieneEscritor = [escritor]
    if productor: nueva_cancion.tieneProductor = [productor]
    
    save_ontology()
    return jsonify({"status": "success", "id": song_id})

@app.route('/api/canciones/<song_id>', methods=['PUT'])
def update_cancion(song_id):
    print(f"🟠 EDITAR canción ID: {song_id}")
    data = request.json
    cancion = onto.search_one(iri=f"*{song_id}")
    if not cancion: return jsonify({"error": "No encontrada"}), 404

    try:
        # Actualizar Datos Simples
        cancion.tieneTituloCancion = [data['titulo']]
        try: cancion.tieneDuracion = [int(data['duracion'])]
        except: pass
        
        # Actualizar Relaciones (Reemplazo total)
        artista = get_or_create("Artista", data['artista'])
        cancion.tieneArtistaPrincipal = [artista]

        genero = get_or_create("Genero", data['genero'])
        cancion.tieneGenero = [genero]
        
        # Discográfica y Album
        discografica = get_or_create("Dsicografia", data.get('discografica'))
        album = get_or_create("Album", data['album'])
        if album:
            album.tieneTituloAlbum = [data['album']]
            album.tieneArtistaPrincipal = [artista]
            album.tieneGenero = [genero]
            if discografica: album.perteneceADiscografica = [discografica]
            # Si el usuario borró la discográfica, limpiamos la relación
            elif not data.get('discografica'): album.perteneceADiscografica = []
                
        cancion.perteneceAAlbum = [album]

        # Secundarios
        comp = get_or_create("Compositor", data.get('compositor'))
        cancion.tieneCompositor = [comp] if comp else []

        esc = get_or_create("Escritor", data.get('escritor'))
        cancion.tieneEscritor = [esc] if esc else []

        prod = get_or_create("productor", data.get('productor'))
        cancion.tieneProductor = [prod] if prod else []

        limpiar_huerfanos() # Limpieza general
        save_ontology()
        return jsonify({"status": "updated"})

    except Exception as e:
        print(f"❌ Error Update: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/canciones/<song_id>', methods=['DELETE'])
def delete_cancion(song_id):
    cancion = onto.search_one(iri=f"*{song_id}")
    if cancion:
        print(f"🔴 ELIMINANDO: {song_id}")
        destroy_entity(cancion)
        limpiar_huerfanos()
        save_ontology()
        return jsonify({"status": "deleted"})
    return jsonify({"error": "No encontrada"}), 404

@app.route('/api/canciones/<song_id>', methods=['GET'])
def get_one_cancion(song_id):
    cancion = onto.search_one(iri=f"*{song_id}")
    if cancion:
        # Reutilizamos lógica de get_canciones para consistencia
        # pero para un solo elemento
        
        album_obj = cancion.perteneceAAlbum[0] if cancion.perteneceAAlbum else None
        discografica = ""
        if album_obj and hasattr(album_obj, 'perteneceADiscografica') and album_obj.perteneceADiscografica:
            disc_obj = album_obj.perteneceADiscografica[0]
            discografica = disc_obj.tieneNombre[0] if disc_obj.tieneNombre else disc_obj.name

        return jsonify({
            "id": cancion.name,
            "titulo": get_safe_property(cancion, "tieneTituloCancion"),
            "artista": get_related_name(cancion, "tieneArtistaPrincipal", "tieneNombre"),
            "album": get_related_name(cancion, "perteneceAAlbum", "tieneTituloAlbum"),
            "genero": get_related_name(cancion, "tieneGenero", "tieneNombre"),
            "duracion": get_safe_property(cancion, "tieneDuracion"),
            "compositor": get_related_name(cancion, "tieneCompositor", "tieneNombre"),
            "escritor": get_related_name(cancion, "tieneEscritor", "tieneNombre"),
            "productor": get_related_name(cancion, "tieneProductor", "tieneNombre"),
            "discografica": discografica
        })
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)