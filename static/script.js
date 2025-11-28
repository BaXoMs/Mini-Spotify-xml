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
            if (!query) {
                renderizarArtistas(data);
                renderizarAlbumes(data);
            }
        })
        .catch(error => console.error('Error:', error));
}

function renderizarCanciones(data) {
    const container = document.getElementById('songs-list-container');
    container.innerHTML = ''; 

    data.forEach(cancion => {
        const fila = document.createElement('div');
        fila.classList.add('song-row');
        // Mostramos los nuevos datos en la tabla
        fila.innerHTML = `
            <div class="col-basic">
                <span class="song-title">${cancion.titulo}</span>
                <span class="song-artist">${cancion.artista}</span>
            </div>
            <div class="col-album">
                <span class="song-album">${cancion.album}</span>
                <span class="song-label"><small>${cancion.discografica || 'Sin disquera'}</small></span>
            </div>
            <div class="col-credits">
                <small>✍️ Comp: ${cancion.compositor || '-'}</small><br>
                <small>📝 Escr: ${cancion.escritor || '-'}</small><br>
                <small>🎚️ Prod: ${cancion.productor || '-'}</small>
            </div>
            <div class="col-meta">
                <span class="badge">${cancion.genero}</span>
                <span class="duration">${cancion.duracion}s</span>
            </div>
            <div class="col-actions">
                <button class="btn-icon edit" data-id="${cancion.id}"><span class="material-icons">edit</span></button>
                <button class="btn-icon delete" data-id="${cancion.id}"><span class="material-icons">delete</span></button>
            </div>
        `;
        container.appendChild(fila);
    });
}

function renderizarArtistas(data) {
    const container = document.getElementById('artists-container');
    container.innerHTML = '';
    const artistasUnicos = [...new Set(data.map(item => item.artista))];

    artistasUnicos.forEach(artista => {
        const card = document.createElement('div');
        card.classList.add('card');
        card.innerHTML = `
            <div class="card-icon"><span class="material-icons">person</span></div>
            <h4>${artista}</h4>
            <p>Artista</p>
        `;
        container.appendChild(card);
    });
}

function renderizarAlbumes(data) {
    const container = document.getElementById('albums-container');
    container.innerHTML = '';
    const albumesMap = new Map();
    data.forEach(item => {
        if (!albumesMap.has(item.album)) albumesMap.set(item.album, item.artista);
    });

    albumesMap.forEach((artista, album) => {
        const card = document.createElement('div');
        card.classList.add('card');
        card.innerHTML = `
            <div class="card-icon"><span class="material-icons">album</span></div>
            <h4>${album}</h4>
            <p>${artista}</p>
        `;
        container.appendChild(card);
    });
}

function configurarBusqueda() {
    const input = document.getElementById('input-busqueda');
    input.addEventListener('input', () => cargarDatos(input.value));
}

function configurarListaCanciones() {
    const container = document.getElementById('songs-list-container');
    container.addEventListener('click', (e) => {
        const btn = e.target.closest('button');
        if (!btn) return;
        
        const id = btn.dataset.id;
        if (btn.classList.contains('delete')) {
            if (confirm('¿Eliminar canción y limpiar referencias?')) {
                fetch(`/api/canciones/${id}`, { method: 'DELETE' })
                    .then(res => res.json())
                    .then(() => cargarDatos(document.getElementById('input-busqueda').value));
            }
        } else if (btn.classList.contains('edit')) {
            fetch(`/api/canciones/${id}`)
                .then(res => res.json())
                .then(cancion => {
                    // Llenar TODOS los campos, incluyendo los nuevos
                    document.getElementById('titulo').value = cancion.titulo;
                    document.getElementById('artista_nombre').value = cancion.artista;
                    document.getElementById('album_titulo').value = cancion.album;
                    document.getElementById('genero').value = cancion.genero;
                    document.getElementById('duracion').value = cancion.duracion;
                    
                    document.getElementById('compositor').value = cancion.compositor || '';
                    document.getElementById('escritor').value = cancion.escritor || '';
                    document.getElementById('productor').value = cancion.productor || '';
                    document.getElementById('discografica').value = cancion.discografica || '';

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
            duracion: document.getElementById('duracion').value,
            // Nuevos campos
            compositor: document.getElementById('compositor').value,
            escritor: document.getElementById('escritor').value,
            productor: document.getElementById('productor').value,
            discografica: document.getElementById('discografica').value
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