from flask import Flask, request, jsonify
from flask_cors import CORS  # Importa CORS
import os
import chardet
from bitarray import bitarray
from collections import deque

app = Flask(__name__)

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        rawdata = f.read(10000)  
        result = chardet.detect(rawdata)
        encoding = result['encoding']
    return encoding

def compress(file_path, output_path):
    dictionary = {}
    print("Comprimiendo...")

    encoding = detect_encoding(file_path)
    
    with open(file_path, 'r', encoding=encoding) as file:
        text = file.read()  
    
    original_size = os.path.getsize(file_path)
    print(f"Capacidad antes de la compresión: {original_size} bytes")

    # Variables
    toCompare = ""
    toStoreInteger = 257
    dq = deque()
    binaryFile = bitarray()

    # Preload ASCII to dictionary
    for i in range(256):
        bitString = bin(i)[2:]
        dictionary[chr(i)] = bitarray(bitString)

    # Algoritmo de compresión
    for letter in text:
        toCompare += letter
        if toCompare in dictionary:
            continue
        else:
            bitString = bin(toStoreInteger)[2:]
            dictionary[toCompare] = bitarray(bitString)
            inDictionary = dictionary[toCompare[:-1]]
            dq.append(inDictionary)
            toCompare = toCompare[-1]
            toStoreInteger += 1
    dq.append(dictionary[text[-1]])

    maxBinLength = len(bin(toStoreInteger)) - 2
    lengthBinary = bin(maxBinLength)[2:]
    lengthFill = 8 - len(lengthBinary)
    aleatoryToFill = bitarray(lengthFill)
    aleatoryToFill.setall(0)
    binaryLengthFile = aleatoryToFill + bitarray(lengthBinary)
    binaryFile += binaryLengthFile

    for value in dq:
        sizeToFill = maxBinLength - len(value)  
        zeroFill = bitarray(sizeToFill)
        zeroFill.setall(0)
        value = zeroFill + value
        binaryFile += value

    with open(output_path, 'wb') as fileBin:
        binaryFile.tofile(fileBin)

    compressed_size = os.path.getsize(output_path)
    print(f"Capacidad después de la compresión: {compressed_size} bytes")
    return compressed_size

def decompress(binary_data, output_path):
    binaryFile = binary_data
    dictionary = {}

    for i in range(256):
        dictionary[i] = chr(i)

    lengthCode = int(binaryFile[0:8].to01(), 2) 
    decompressed = ''
    key = 257
    lastString = ''
    lastString = getStringFromBeginBinaryCode(8, lengthCode, dictionary, binaryFile)
    decompressed += lastString
    for begin in range(8 + lengthCode, len(binaryFile) - lengthCode, lengthCode):
        inputString = getStringFromBeginBinaryCode(begin, lengthCode, dictionary, binaryFile)

        if inputString:
            dictionary[key] = lastString + inputString[0]
            decompressed += inputString
            lastString = inputString
        else:
            dictionary[key] = lastString + lastString[0]
            decompressed += dictionary[key]
            lastString = dictionary[key]
        key += 1

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(decompressed)
    print(f"Descompresión completa. Archivo guardado como: {output_path}")

def getStringFromBeginBinaryCode(begin, lengthCode, dictionary, binaryFile):
    code = binaryFile[begin:begin + lengthCode]
    codeInt = int(code.to01(), 2)
    stringFromCode = dictionary.get(codeInt)
    return stringFromCode


app = Flask(__name__)
CORS(app)  

@app.route('/compress', methods=['POST'])
def compress_endpoint():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        input_file = f"./uploads/{file.filename}"
        output_file = f"./compressed/{file.filename}.bin"
        
        file.save(input_file)  
        
        compressed_size = compress(input_file, output_file)
        
        return jsonify({
            'message': 'Compresión completa',
            'compressed_size': compressed_size
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decompress', methods=['POST'])
def decompress_endpoint():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        input_file = f"./compressed/{file.filename}"
        output_file = f"./decompressed/{file.filename}.txt"
        
        file.save(input_file) 
        
        binary_data = bitarray()
        with open(input_file, 'rb') as fileBits:
            binary_data.fromfile(fileBits)
        
        decompress(binary_data, output_file)
        return jsonify({'message': 'Descompresión completa'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)