document.addEventListener('DOMContentLoaded', function() {
    cargarCanciones();
    configurarFormulario();
    configurarListaCanciones(); // Renombrado de configurarTabla
    configurarBusqueda();
});

// MODIFICADA: Ahora crea DIVs en lugar de filas de tabla <tr>
function cargarCanciones(query = '') {
    const songsContainer = document.getElementById('songs-list-container');
    const url = `/api/canciones?q=${encodeURIComponent(query)}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Limpiamos solo las filas de canciones, no la cabecera
            const existingRows = songsContainer.querySelectorAll('.song-row');
            existingRows.forEach(row => row.remove());

            data.forEach(cancion => {
                // Creamos un div con la clase 'song-row'
                const fila = document.createElement('div');
                fila.classList.add('song-row');
                
                // Usamos la estructura de divs que coincide con tu CSS
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
                songsContainer.appendChild(fila);
            });
        })
        .catch(error => console.error('Error al cargar las canciones:', error));
}

// NUEVA: Configura la barra de búsqueda
function configurarBusqueda() {
    const inputBusqueda = document.getElementById('input-busqueda');
    inputBusqueda.addEventListener('input', function() {
        cargarCanciones(inputBusqueda.value);
    });
}

// Renombrada y adaptada para el nuevo contenedor de canciones
function configurarListaCanciones() {
    document.getElementById('songs-list-container').addEventListener('click', function(event) {
        const target = event.target;
        const cancionId = target.dataset.id;

        if (target.classList.contains('btn-eliminar')) {
            if (confirm('¿Estás seguro de que quieres eliminar esta canción?')) {
                fetch(`/api/canciones/${cancionId}`, { method: 'DELETE' })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Eliminado:', data);
                        cargarCanciones(document.getElementById('input-busqueda').value);
                    });
            }
        } else if (target.classList.contains('btn-editar')) {
            fetch(`/api/canciones/${cancionId}`)
                .then(response => response.json())
                .then(cancion => {
                    document.getElementById('titulo').value = cancion.titulo;
                    document.getElementById('artista_nombre').value = cancion.artista;
                    document.getElementById('album_titulo').value = cancion.album;
                    document.getElementById('genero').value = cancion.genero;
                    document.getElementById('duracion').value = cancion.duracion;

                    const form = document.getElementById('form-anadir-cancion');
                    form.dataset.editingId = cancion.id;
                    form.querySelector('button').textContent = 'Actualizar Canción';
                });
        }
    });
}

// Las funciones de formulario no necesitan cambios
function configurarFormulario() {
    const form = document.getElementById('form-anadir-cancion');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const cancionId = form.dataset.editingId;
        const cancionData = {
            titulo: document.getElementById('titulo').value,
            artista: document.getElementById('artista_nombre').value,
            album: document.getElementById('album_titulo').value,
            genero: document.getElementById('genero').value,
            duracion: document.getElementById('duracion').value
        };
        const query = document.getElementById('input-busqueda').value;

        const isUpdating = !!cancionId;
        const url = isUpdating ? `/api/canciones/${cancionId}` : '/api/canciones';
        const method = isUpdating ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cancionData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Éxito:', data);
            resetFormulario();
            cargarCanciones(query);
        });
    });
}

function resetFormulario() {
    const form = document.getElementById('form-anadir-cancion');
    form.reset();
    delete form.dataset.editingId;
    form.querySelector('button').textContent = 'Guardar Canción';
}