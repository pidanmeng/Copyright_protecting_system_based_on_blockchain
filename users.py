# coding=utf-8
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii


class Users:
    def __init__(self, nodeId):
        self.privateKey = None
        self.publicKey = None
        self.nodeId = nodeId

    @staticmethod
    def generateKeys():
        privateKey = RSA.generate(1024, Crypto.Random.new().read)
        publicKey = privateKey.publickey()
        return binascii.hexlify(privateKey.exportKey(format='DER')).decode('ascii'), binascii.hexlify(
            publicKey.exportKey(format='DER')).decode('ascii')

    def saveKeys(self):
        try:
            with open('user-{}.txt'.format(self.nodeId), mode='w') as f:
                f.write(self.publicKey)
                f.write('\n')
                f.write(self.privateKey)
            return True
        except (IOError, IndexError):
            print('用户公私钥存储失败')
            return False

    def createKeys(self):
        privateKey, publicKey = self.generateKeys()
        self.privateKey = privateKey
        self.publicKey = publicKey

    def loadKeys(self):
        try:
            with open('user-{}.txt'.format(self.nodeId), mode='r') as f:
                keys = f.readlines()
                self.publicKey = keys[0][:-1]
                self.privateKey = keys[1]
            return True
        except(IOError, IndexError):
            print('用户公私钥读取失败')
            return False

    def signTransaction(self, copyrightOwner, picUrl, picPhash):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.privateKey)))
        h = SHA256.new((str(copyrightOwner) + str(picUrl) + str(picPhash)).encode('utf8'))
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verifyTransaction(transaction):
        publicKey = RSA.importKey(binascii.unhexlify(transaction.copyrightOwner))
        verifier = PKCS1_v1_5.new(publicKey)

        h = SHA256.new(
            (str(transaction.copyrightOwner) + str(transaction.picUrl) + str(transaction.picPhash)).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(transaction.signature))
