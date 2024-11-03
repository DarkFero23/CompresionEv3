def generate_large_text_file(filename, size_in_mb):
    size_in_bytes = size_in_mb * 1024 * 1024 
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("Este es un texto de prueba para comprimir. " * 500)  
        while file.tell() < size_in_bytes:
            file.write("Este es un texto de prueba para comprimir. ")  
generate_large_text_file("D:/Compresion/BACKEND/large_file.txt", 500)
