from arc4 import ARC4
import base64
import zlib
import requests
import os

CRYPT_KEY = "redacted"

def decrypt(base64Packet,key=CRYPT_KEY):
    arc4 = ARC4(key)
    encryptedPacket = base64.decodebytes(str.encode(base64Packet))
    decryptedPacket = arc4.decrypt(encryptedPacket)
    try:
        unzippedPacket = zlib.decompress(decryptedPacket)
        return unzippedPacket.decode("utf-8")
    except Exception:
        pass
    return (decryptedPacket.decode("utf-8"))

def encrypt(plaintextPacket,key=CRYPT_KEY):
    arc4 = ARC4(key)
    encryptedPacket = arc4.encrypt(plaintextPacket)
    base64Packet = base64.encodebytes(encryptedPacket)
    return base64Packet.decode("utf-8")

def findKey(cyphertext,wasmDataURL):
    plaintext = """{"config.gC":{"bw":-1}}"""
    wasmRequest = requests.get(wasmDataURL)
    wasmFile = open('farm.wasm.gz', 'wb')
    wasmFile.write(wasmRequest.content)
    wasmFile.close()
    os.popen("gzip -d --force farm.wasm.gz")
    strings = os.popen("strings farm.wasm | awk 'length($0)==40'")
    os.popen("rm -f farm.wasm")
    for string in strings:
        try:
            key = string.strip()
            if decrypt(cyphertext,key) == plaintext:
                return key
        except:
            continue
    return None
