# coding=utf-8
from utility.hashUtil import hashBlock, hashString256
from users import Users
from utility.DHash import DHash, url_to_image


class Verification:

    def __init__(self):
        pass

    @staticmethod
    def validProof(transactions, lastHash, proof):
        """检查工作量证明"""
        guess = (str([tx.toOrderedDict() for tx in transactions]) + str(lastHash) + str(proof)).encode()
        guessHash = hashString256(guess)
        print str([tx.toOrderedDict() for tx in transactions])
        print str(lastHash)
        print str(proof)
        print guessHash
        return guessHash[0:3] == '000'

    @classmethod
    def verifyChain(cls, blockChain):
        """检查区块链合法性"""
        for (index, block) in enumerate(blockChain):
            if index == 0:
                continue
            if block.previousHash != hashBlock(blockChain[index - 1]):
                print 'previousHashErr'
                return False
            if not cls.validProof(block.transactions, block.previousHash, block.proof):
                print('工作量证明错误')
                return False
        return True

    @staticmethod
    def verifyTransaction(blockChain, openTransactions, transaction, checkPhash=True):
        """事务有效性验证验证逻辑"""
        # 对图片和Phash进行比对
        if checkPhash:
            phash = DHash.calculate_hash(url_to_image(transaction.picUrl))

            for block in blockChain:
                for tx in block.transactions:
                    if DHash.hamming_distance(str(tx.picPhash), str(phash)):
                        return False

            for tx in openTransactions:
                if DHash.hamming_distance(str(tx.picPhash), str(phash)):
                    return False

            return phash == transaction.picPhash and Users.verifyTransaction(transaction)
        else:
            return Users.verifyTransaction(transaction)

    # @classmethod
    # def verifyTransactions(cls, openTransactions):
    #     return all([cls.verifyTransaction(tx, False) for tx in openTransactions])
