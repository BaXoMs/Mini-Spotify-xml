document.addEventListener('DOMContentLoaded', function() {
    cargarDatos();
    configurarFormulario();
    configurarListaCanciones();
    configurarBusqueda();
});

function cargarDatos(query = '') {
    const url = `/api/canciones?q=${encodeURIComponent(query)}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            renderizarCanciones(data);
            if (!query) { // Solo regeneramos artistas/albumes si no estamos filtrando
                renderizarArtistas(data);
                renderizarAlbumes(data);
            }
        })
        .catch(error => console.error('Error:', error));
}

function renderizarCanciones(data) {
    const container = document.getElementById('songs-list-container');
    // Limpiamos filas viejas
    const existingRows = container.querySelectorAll('.song-row');
    existingRows.forEach(row => row.remove());

    data.forEach(cancion => {
        const fila = document.createElement('div');
        fila.classList.add('song-row');
        fila.innerHTML = `
            <div class="title">${cancion.titulo}</div>
            <div>
                <span class="song-artist">${cancion.artista}</span><br/>
                <span class="song-album">${cancion.album}</span>
            </div>
            <div><span class="genre-tag">${cancion.genero}</span></div>
            <div class="song-duration">${cancion.duracion}</div>
            <div>
                <button class="btn-editar" data-id="${cancion.id}">Editar</button>
                <button class="btn-eliminar" data-id="${cancion.id}">Eliminar</button>
            </div>
        `;
        container.appendChild(fila);
    });
}

function renderizarArtistas(data) {
    const container = document.getElementById('artists-container');
    container.innerHTML = '';
    
    // Extraemos artistas únicos
    const artistasUnicos = [...new Set(data.map(item => item.artista))];

    artistasUnicos.forEach(artista => {
        const card = document.createElement('div');
        card.classList.add('artist-card');
        card.innerHTML = `
            <div class="artist-avatar">${artista.charAt(0)}</div>
            <h3>${artista}</h3>
            <p class="country">Artista</p>
        `;
        container.appendChild(card);
    });
}

function renderizarAlbumes(data) {
    const container = document.getElementById('albums-container');
    container.innerHTML = '';

    // Extraemos álbumes únicos (usamos un mapa para evitar duplicados por nombre)
    const albumesMap = new Map();
    data.forEach(item => {
        if (!albumesMap.has(item.album)) {
            albumesMap.set(item.album, item.artista);
        }
    });

    albumesMap.forEach((artista, album) => {
        const card = document.createElement('div');
        card.classList.add('album-card');
        card.innerHTML = `
            <div class="album-cover">${album.charAt(0)}</div>
            <div class="album-info">
                <h3>${album}</h3>
                <div class="album-id">${artista}</div>
            </div>
        `;
        container.appendChild(card);
    });
}

// --- CONFIGURACIONES DE EVENTOS (Igual que antes) ---

function configurarBusqueda() {
    const input = document.getElementById('input-busqueda');
    const form = document.getElementById('form-busqueda');

    input.addEventListener('input', () => cargarDatos(input.value));
    
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            document.getElementById('seccion-canciones')?.scrollIntoView({ behavior: 'smooth' });
        }
    });

    form?.addEventListener('submit', e => e.preventDefault());
}

function configurarListaCanciones() {
    const container = document.getElementById('songs-list-container');
    if (!container) return;

    container.addEventListener('click', (e) => {
        const target = e.target;
        const id = target.dataset.id;

        if (target.classList.contains('btn-eliminar')) {
            if (confirm('¿Eliminar canción?')) {
                fetch(`/api/canciones/${id}`, { method: 'DELETE' })
                    .then(res => res.json())
                    .then(() => cargarDatos(document.getElementById('input-busqueda').value));
            }
        } else if (target.classList.contains('btn-editar')) {
            fetch(`/api/canciones/${id}`)
                .then(res => res.json())
                .then(cancion => {
                    document.getElementById('titulo').value = cancion.titulo;
                    document.getElementById('artista_nombre').value = cancion.artista;
                    document.getElementById('album_titulo').value = cancion.album;
                    document.getElementById('genero').value = cancion.genero;
                    document.getElementById('duracion').value = cancion.duracion;

                    const form = document.getElementById('form-anadir-cancion');
                    form.dataset.editingId = cancion.id;
                    form.querySelector('button').textContent = 'Actualizar Canción';
                    form.scrollIntoView({ behavior: 'smooth' });
                });
        }
    });
}

function configurarFormulario() {
    const form = document.getElementById('form-anadir-cancion');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const id = form.dataset.editingId;
        const data = {
            titulo: document.getElementById('titulo').value,
            artista: document.getElementById('artista_nombre').value,
            album: document.getElementById('album_titulo').value,
            genero: document.getElementById('genero').value,
            duracion: document.getElementById('duracion').value
        };

        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/canciones/${id}` : '/api/canciones';

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(() => {
            form.reset();
            delete form.dataset.editingId;
            form.querySelector('button').textContent = 'Guardar Canción';
            cargarDatos();
        });
    });
}