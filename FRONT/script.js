document.getElementById('compress-btn').addEventListener('click', function() {
    const fileInput = document.getElementById('file-input-compress');
    const file = fileInput.files[0];
    if (!file) {
        alert('Por favor selecciona un archivo para comprimir.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('http://localhost:5000/compress', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(data => {
        document.getElementById('compress-result').innerText = `Archivo comprimido guardado como: ${data.output_file}, tamaño: ${data.compressed_size} bytes`;
    })
    .catch(error => {
        console.error('Error al comprimir:', error);
    });
});
// Función para descomprimir archivos
document.getElementById('decompress-btn').addEventListener('click', function() {
    const fileInput = document.getElementById('file-input-decompress');
    const file = fileInput.files[0];
    if (!file) {
        alert('Por favor selecciona un archivo para descomprimir.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('http://localhost:5000/decompress', {  // Endpoint para descompresión
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(data => {
        document.getElementById('decompress-result').innerText = `Archivo descomprimido guardado como: ${data.output_file}`;
    })
    .catch(error => {
        console.error('Error al descomprimir:', error);
    });
});