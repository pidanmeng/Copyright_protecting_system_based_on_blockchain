# coding=utf-8
from time import time
from utility.printable import Printable


class Block(Printable):
    def __init__(self, index, previousHash, transactions, proof, timestamp=time()):
        self.index = index
        self.previousHash = previousHash
        self.timestamp = timestamp
        self.transactions = transactions
        self.proof = proof

    # def printBlock(self):
    #     print('%s%s%s%s%s%s%s%s%s'%
    #         ('\tindex:',self.index,
    #         '\n\tpreviousHash:',self.previousHash,
    #         '\n\ttimestamp:',self.timestamp,
    #         '\n\tproof:',self.proof,
    #         '\n\ttransactions:'))
    #     for tx in range(len(self.transactions)):
    #         print('%s%s'%('\t\tindex:',tx))
    #         self.transactions[tx].printTransactions()
