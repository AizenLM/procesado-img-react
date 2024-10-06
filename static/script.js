document.getElementById('formImagen').addEventListener('submit', function(event) {
    event.preventDefault();  // Evita que el formulario se envíe automáticamente

    // Crear el formulario para enviar la imagen
    const formData = new FormData();
    const archivoImagen = document.getElementById('imagen').files[0];
    const traslape = document.getElementById('traslape').checked;

    if (!archivoImagen) {
        alert('Por favor, selecciona una imagen');
        return;
    }

    formData.append('imagen', archivoImagen);
    formData.append('con_traslape', traslape);

    // Enviar la imagen al servidor Flask
    fetch('http://127.0.0.1:5000/procesar_imagen', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Mostrar los resultados en el frontend
        const resultadoDiv = document.getElementById('resultado');
        resultadoDiv.innerHTML = '<h2>Regiones detectadas:</h2>';
        resultadoDiv.innerHTML += JSON.stringify(data.regiones);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al procesar la imagen');
    });
});
