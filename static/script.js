// Espera a que todo el contenido de la página HTML se haya cargado
document.addEventListener('DOMContentLoaded', function() {
    
    // Busca el cuerpo de la tabla en el HTML
    const tablaBody = document.getElementById('tabla-canciones-body');

    // Usa la API 'fetch' para pedir los datos a nuestro backend en la ruta '/api/canciones'
    fetch('/api/canciones')
        .then(response => response.json()) // Convierte la respuesta a formato JSON
        .then(data => {
            // 'data' es ahora una lista de objetos, cada uno es una canción
            
            // Limpiamos la tabla por si tuviera algo
            tablaBody.innerHTML = ''; 

            // Recorremos cada canción en la lista de datos
            data.forEach(cancion => {
                // Creamos una nueva fila <tr>
                const fila = document.createElement('tr');
                
                // Creamos y añadimos las celdas <td> para cada dato de la canción
                fila.innerHTML = `
                    <td>${cancion.titulo}</td>
                    <td>${cancion.artista}</td>
                    <td>${cancion.album}</td>
                    <td>${cancion.genero}</td>
                    <td>${cancion.duracion}</td>
                `;
                
                // Añadimos la fila completa al cuerpo de la tabla
                tablaBody.appendChild(fila);
            });
        })
        .catch(error => console.error('Error al cargar las canciones:', error));
});

// 1. Obtener el formulario del HTML
const formAnadir = document.getElementById('form-anadir-cancion');

// 2. Añadir un 'escuchador' para el evento 'submit'
formAnadir.addEventListener('submit', function(event) {
    // Prevenir que la página se recargue, que es el comportamiento por defecto del formulario
    event.preventDefault();

    // 3. Recoger los datos de los campos del formulario
    const nuevaCancion = {
        titulo: document.getElementById('titulo').value,
        artista: document.getElementById('artista_nombre').value, // ¡Línea añadida!
        album: document.getElementById('album_titulo').value,
        genero: document.getElementById('genero').value,
        duracion: document.getElementById('duracion').value
    };

    // 4. Enviar los datos al backend usando fetch con el método POST
    fetch('/api/canciones', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(nuevaCancion) // Convertimos el objeto a un string JSON
    })
    .then(response => response.json())
    .then(data => {
        console.log('Éxito:', data);
        // Limpiar el formulario
        formAnadir.reset();
        // Volver a cargar la tabla para que aparezca la nueva canción
        cargarCanciones(); // Reutilizamos la función que ya teníamos
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

// Cambiamos el código original para que sea una función reutilizable
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
                `;
                tablaBody.appendChild(fila);
            });
        })
        .catch(error => console.error('Error al cargar las canciones:', error));
}

// Llamada inicial para cargar la tabla cuando la página se abre
document.addEventListener('DOMContentLoaded', cargarCanciones);