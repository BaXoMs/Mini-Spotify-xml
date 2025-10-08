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