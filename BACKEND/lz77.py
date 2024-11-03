import chardet  
from bitarray import bitarray
from collections import deque
import os  

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
    lengthBinary = 0

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

    # Armar cadena de ceros
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
    print(f"Compresión completa. Archivo guardado como: {output_path}")

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

# Comprimir
input_file = "D:\\Compresion\\BACKEND\\Prueba.txt"
output_file_compressed = "D:\\Compresion\\BACKEND\\salida.bin"
compress(input_file, output_file_compressed)

#Descomprimir
#input_file_compressed = "ruta/al/archivo/salida.bin"
#output_file_decompressed = "ruta/al/archivo/salida.txt"
#binary_data = bitarray()
#with open(input_file_compressed, 'rb') as fileBits:
 #   binary_data.fromfile(fileBits)

#decompress(binary_data, output_file_decompressed)
