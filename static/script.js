document.addEventListener('DOMContentLoaded', function() {
    cargarCanciones();
    configurarFormulario();
    configurarListaCanciones(); // Renombrado de configurarTabla
    configurarBusqueda();
});

// MODIFICADA: Ahora crea DIVs en lugar de filas de tabla <tr>
function cargarCanciones(query = '') {
    const songsContainer = document.getElementById('songs-list-container');
    // Si la API falla o no existe, usa la ruta que tengas configurada
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

// MODIFICADA: Ahora incluye la lógica del ENTER para hacer scroll
function configurarBusqueda() {
    const inputBusqueda = document.getElementById('input-busqueda');
    const formBusqueda = document.getElementById('form-busqueda');

    // 1. Búsqueda en tiempo real (mientras escribes)
    inputBusqueda.addEventListener('input', function() {
        cargarCanciones(inputBusqueda.value);
    });

    // 2. NUEVO: Al presionar Enter, baja a la sección de canciones
    inputBusqueda.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Evita que se recargue la página
            
            // Busca la sección por el ID que pusimos en el XSL nuevo
            const seccionCanciones = document.getElementById('seccion-canciones');
            
            if (seccionCanciones) {
                seccionCanciones.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }
        }
    });

    // 3. Prevenir envío tradicional del formulario
    if (formBusqueda) {
        formBusqueda.addEventListener('submit', function(e) {
            e.preventDefault();
        });
    }
}

// Renombrada y adaptada para el nuevo contenedor de canciones
function configurarListaCanciones() {
    const container = document.getElementById('songs-list-container');
    if (!container) return; // Validación por seguridad

    container.addEventListener('click', function(event) {
        const target = event.target;
        const cancionId = target.dataset.id;

        if (target.classList.contains('btn-eliminar')) {
            if (confirm('¿Estás seguro de que quieres eliminar esta canción?')) {
                fetch(`/api/canciones/${cancionId}`, { method: 'DELETE' })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Eliminado:', data);
                        cargarCanciones(document.getElementById('input-busqueda').value);
                        // Opcional: Recargar la página completa si quieres actualizar artistas/albumes
                        // window.location.reload(); 
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
                    
                    // Opcional: subir scroll al formulario al dar editar
                    form.scrollIntoView({ behavior: 'smooth' });
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
            // Si quieres que se actualicen las tarjetas de artistas/albumes nuevos, descomenta:
            window.location.reload(); 
            // Si solo quieres actualizar la tabla sin recargar:
            // cargarCanciones(query);
        });
    });
}

function resetFormulario() {
    const form = document.getElementById('form-anadir-cancion');
    form.reset();
    delete form.dataset.editingId;
    form.querySelector('button').textContent = 'Guardar Canción';
}