# coding=utf-8
import json
import pickle
import requests

from block import Block
from utility.hashUtil import hashBlock
from transaction import Transaction
from utility.verification import Verification, DHash
from users import Users

DEBUG_MODE = True


class BlockChain:
    def __init__(self, publicKey, nodeId):
        # 定义创世区块
        genesisBlock = Block(0, '', [], 100, 0)
        # 定义区块链
        self.__chain = [genesisBlock]
        # 定义事务列表
        self.__openTransactions = []
        # 加载区块链

        self.publicKey = publicKey
        self.__peerNodes = set()
        self.nodeId = nodeId
        self.resolveConflicts = False
        self.loadData()

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def getChain(self):
        return self.__chain[:]

    def getOpenTransactions(self):
        return self.__openTransactions

    def saveData(self):
        """保存区块链与transaction队列"""
        try:
            if not DEBUG_MODE:
                with open("blockchain-{}.p".format(self.nodeId), mode="wb") as f:

                    saveableData = {
                        'chain': self.__chain,
                        'ot': self.__openTransactions,
                        'peerNodes': self.__peerNodes
                    }
                    f.write(pickle.dumps(saveableData))
            elif DEBUG_MODE:
                with open("blockchain-{}.txt".format(self.nodeId), mode="w") as f:
                    saveableChain = [block.__dict__ for block in [
                        Block(block.index, block.previousHash, [tx.__dict__ for tx in block.transactions],
                              block.proof, block.timestamp) for block in self.__chain]]
                    f.write(json.dumps(saveableChain))
                    f.write('\n')
                    saveableTx = [tx.__dict__ for tx in self.__openTransactions]
                    f.write(json.dumps(saveableTx))
                    f.write('\n')
                    f.write(json.dumps(list(self.__peerNodes)))
        except (IOError, IndexError):
            print('存储区块链失败')

    def loadData(self):
        """加载区块链"""
        try:
            if not DEBUG_MODE:
                with open("blockchain-{}.p".format(self.nodeId), mode="rb") as f:
                    fileContent = pickle.loads(f.read())
                    self.__chain = fileContent['chain']
                    self.__openTransactions = fileContent['ot']
                    self.__peerNodes = fileContent['peerNodes']
            elif DEBUG_MODE:
                with open("blockchain-{}.txt".format(self.nodeId), mode="r") as f:
                    fileContent = f.readlines()
                    blockChain = json.loads(fileContent[0][:-1])

                    self.__chain = [Block(
                        block['index'],
                        block['previousHash'],
                        [Transaction(tx['copyrightOwner'], tx['picUrl'], tx['signature'], tx['picPhash']) for tx in
                         block['transactions']],
                        # [OrderedDict([("copyrightOwner", tx['copyrightOwner']),("picUrl", tx['picUrl']),("picPhash",
                        # tx['picPhash'])]) for tx in block['transactions']],
                        block['proof'],
                        block['timestamp']
                    ) for block in blockChain]

                    openTransactions = json.loads(fileContent[1][:-1])
                    self.__openTransactions = [
                        Transaction(tx['copyrightOwner'], tx['picUrl'], tx['signature'], tx['picPhash']) for tx in
                        openTransactions]
                    peerNodes = json.loads(fileContent[2])
                    self.__peerNodes = set(peerNodes)
        except (IOError, IndexError):
            self.__openTransactions = []
            self.__peerNodes = set([])
            self.saveData()
            print('未找到区块链文件\n已创建新区块链')

    def proofOfWork(self):
        """
        工作量证明
        为返回一个Nouse使当区块hash之后前三位为0
        """
        lastBlock = self.__chain[-1]
        lastHash = hashBlock(lastBlock)
        proof = 0
        while not Verification.validProof(self.__openTransactions, lastHash, proof):
            proof += 1
        print('proof = ' + str(proof))
        return proof

    def getCopyrightInfo(self, copyrightOwner=None):
        if copyrightOwner is None:
            if self.publicKey is None:
                return None
            user = self.publicKey
        else:
            user = copyrightOwner

        txpicUrl = []
        for block in self.__chain:
            for tx in block.transactions:
                if tx.copyrightOwner == user:
                    txpicUrl.append(tx.picUrl)

        for tx in self.__openTransactions:
            if tx.copyrightOwner == user:
                txpicUrl.append(tx.picUrl)

        return txpicUrl

    def addTransaction(self, copyrightOwner, picUrl, signature, picPhash, isReceiving=False):
        """
        向事务队列添加新事务
        :param isReceiving: 标志是否为被广播的事务
        :param copyrightOwner: 版权所有人
        :param picUrl:图片ID
        :param signature:数字签名
        :param picPhash:图片PHash
        """
        # if self.publicKey is None:
        #     return False
        transaction = Transaction(copyrightOwner, picUrl, signature, picPhash)

        # transaction =  OrderedDict(
        #     [
        #         ("copyrightOwner",copyrightOwner),
        #         ("picUrl",picUrl),
        #         ("picPhash",picPhash)
        #     ])

        if Verification.verifyTransaction(self.__chain, self.__openTransactions, transaction):
            self.__openTransactions.append(transaction)
            self.saveData()
            # 主动广播
            if not isReceiving:
                for node in self.__peerNodes:
                    url = 'http://{}/broadcastTransaction'.format(node)
                    try:
                        response = requests.post(url, json={
                            'copyrightOwner': copyrightOwner,
                            'picUrl': picUrl,
                            'picPhash': picPhash,
                            'signature': signature
                        })
                        if response.status_code == 400 or response.status_code == 500:
                            print('请求不合法或事务添加失败')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    def isPhashInChain(self, phash):
        for block in self.__chain:
            for tx in block.transactions:
                if DHash.hamming_distance(str(tx.picPhash), str(phash)):
                    return True

        for tx in self.__openTransactions:
            print(type(tx.picPhash))
            if DHash.hamming_distance(str(tx.picPhash), str(phash)):
                return True

    @property
    def mineBlock(self):
        """挖掘一个区块"""
        if self.publicKey is None:
            return None
        lastBlock = self.__chain[-1]
        hashedBlock = hashBlock(lastBlock)
        proof = self.proofOfWork()
        copiedTransactions = self.__openTransactions[:]

        for tx in copiedTransactions:
            if not Users.verifyTransaction(tx):
                return None

        block = Block(len(self.__chain), hashedBlock, copiedTransactions, proof)

        self.__chain.append(block)
        self.__openTransactions = []
        self.saveData()
        for node in self.__peerNodes:
            url = 'http://{}/broadcastBlock'.format(node)
            convertedBlock = block.__dict__.copy()
            convertedBlock['transactions'] = [tx.__dict__ for tx in convertedBlock['transactions']]
            try:
                response = requests.post(url, json={'block': convertedBlock})
                if response.status_code == 400 or response.status_code == 500:
                    print('请求不合法或区块添加失败')
                if response.status_code == 409:
                    self.resolveConflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return block

    def addBlock(self, block):
        transactions = [Transaction(tx['copyrightOwner'], tx['picUrl'], tx['signature'], tx['picPhash'])
                        for tx in block['transactions']]
        proofIsValid = Verification.validProof(transactions, block['previousHash'], block['proof'])
        hashesMatch = hashBlock(self.__chain[-1]) == block['previousHash']
        print proofIsValid
        print hashesMatch
        if not proofIsValid or not hashesMatch:
            return False
        convertedBlock = Block(block['index'], block['previousHash'], transactions, block['proof'], block['timestamp'])
        self.__chain.append(convertedBlock)
        storedTransactions = self.__openTransactions[:]
        for itx in block['transactions']:
            for opentx in storedTransactions:
                if opentx.copyrightOwner == itx['copyrightOwner'] and \
                        opentx.picUrl == itx['picUrl'] and \
                        opentx.picPhash == itx['picPhash'] and opentx.signature == itx['signature']:
                    try:
                        self.__openTransactions.remove(opentx)
                    except ValueError:
                        print('事务已被移除')
        self.saveData()
        return True

    def resolve(self):
        winnerChain = self.__chain
        replace = False
        for node in self.__peerNodes:
            url = 'http://{}/chain'.format(node)
            # try:
            response = requests.get(url)
            nodeChain = response.json()
            nodeChain = [Block(block['index'], block['previousHash'],
                               [Transaction(tx['copyrightOwner'], tx['picUrl'], tx['signature'], tx['picPhash'])
                                for tx in block['transactions']], block['proof'], block['timestamp']) for block in
                         nodeChain]
            nodeChainLength = len(nodeChain)
            localChainLength = len(winnerChain)
            print nodeChainLength > localChainLength
            print Verification.verifyChain(nodeChain)
            if nodeChainLength > localChainLength and Verification.verifyChain(nodeChain):
                winnerChain = nodeChain
                replace = True
            # except requests.exceptions.ConnectionError:
            #     print 'requestsErr'
            #     continue
        self.resolveConflicts = False
        self.__chain = winnerChain
        if replace:
            self.__openTransactions = []
        self.saveData()
        return replace

    def addPeerNode(self, node):
        print(self.__peerNodes)
        self.__peerNodes.add(node)
        self.saveData()

    def removePeerNode(self, node):
        self.__peerNodes.discard(node)
        self.saveData()

    def getPeerNodes(self):
        return list(self.__peerNodes)[:]
