document.addEventListener('DOMContentLoaded', function() {
    cargarCanciones();
    configurarFormulario();
    configurarTabla();
});

function cargarCanciones() {
    const tablaBody = document.getElementById('tabla-canciones-body');
    fetch('/api/canciones')
        .then(response => response.json())
        .then(data => {
            tablaBody.innerHTML = '';
            data.forEach(cancion => {
                const fila = document.createElement('tr');
                fila.innerHTML = `
                    <td>${cancion.titulo}</td>
                    <td>${cancion.artista}</td>
                    <td>${cancion.album}</td>
                    <td>${cancion.genero}</td>
                    <td>${cancion.duracion}</td>
                    <td>
                        <button class="btn-editar" data-id="${cancion.id}">Editar</button>
                        <button class="btn-eliminar" data-id="${cancion.id}">Eliminar</button>
                    </td>
                `;
                tablaBody.appendChild(fila);
            });
        })
        .catch(error => console.error('Error al cargar las canciones:', error));
}

function configurarFormulario() {
    const form = document.getElementById('form-anadir-cancion');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const cancionId = form.dataset.editingId; // Verificamos si estamos editando
        
        const cancionData = {
            titulo: document.getElementById('titulo').value,
            artista: document.getElementById('artista_nombre').value,
            album: document.getElementById('album_titulo').value,
            genero: document.getElementById('genero').value,
            duracion: document.getElementById('duracion').value
        };

        if (cancionId) {
            // --- MODO ACTUALIZAR ---
            fetch(`/api/canciones/${cancionId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(cancionData)
            })
            .then(response => response.json())
            .then(data => {
                console.log('Éxito (Update):', data);
                resetFormulario();
                cargarCanciones();
            })
            .catch(error => console.error('Error al actualizar:', error));
        } else {
            // --- MODO AÑADIR (como antes) ---
            fetch('/api/canciones', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(cancionData)
            })
            .then(response => response.json())
            .then(data => {
                console.log('Éxito (Create):', data);
                resetFormulario();
                cargarCanciones();
            })
            .catch(error => console.error('Error al crear:', error));
        }
    });
}

function configurarTabla() {
    document.getElementById('tabla-canciones-body').addEventListener('click', function(event) {
        const target = event.target;
        const cancionId = target.dataset.id;

        if (target.classList.contains('btn-eliminar')) {
            // --- LÓGICA DE ELIMINAR (como antes) ---
            if (confirm('¿Estás seguro de que quieres eliminar esta canción?')) {
                fetch(`/api/canciones/${cancionId}`, { method: 'DELETE' })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Eliminado:', data);
                        cargarCanciones();
                    })
                    .catch(error => console.error('Error al eliminar:', error));
            }
        } else if (target.classList.contains('btn-editar')) {
            // --- LÓGICA DE EDITAR ---
            fetch(`/api/canciones/${cancionId}`)
                .then(response => response.json())
                .then(cancion => {
                    // Llenar el formulario con los datos de la canción
                    document.getElementById('titulo').value = cancion.titulo;
                    document.getElementById('artista_nombre').value = cancion.artista;
                    document.getElementById('album_titulo').value = cancion.album;
                    document.getElementById('genero').value = cancion.genero;
                    document.getElementById('duracion').value = cancion.duracion;

                    // Poner el formulario en "modo edición"
                    const form = document.getElementById('form-anadir-cancion');
                    form.dataset.editingId = cancion.id; // Guardamos el ID en el formulario
                    form.querySelector('button').textContent = 'Actualizar Canción';
                })
                .catch(error => console.error('Error al obtener datos para editar:', error));
        }
    });
}

function resetFormulario() {
    const form = document.getElementById('form-anadir-cancion');
    form.reset(); // Limpia los campos
    delete form.dataset.editingId; // Quitamos el ID del modo edición
    form.querySelector('button').textContent = 'Guardar Canción';
}