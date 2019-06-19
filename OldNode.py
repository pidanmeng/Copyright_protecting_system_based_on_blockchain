# coding=utf-8
# from uuid import uuid4

from blockChain import BlockChain
from utility.verification import Verification
from users import Users


class Node:

    def __init__(self):
        # self.user = str(uuid4())
        self.user = Users()
        self.user.createKeys()
        self.blockChain = BlockChain(self.user.publicKey)

    @staticmethod
    def getTransactionValue():
        """获取当前事务信息"""
        txpicUrl = input("请输入图片ID")
        txPicphash = input("请输入图片PHash")
        return txpicUrl, txPicphash

    def printAllBlock(self):
        """"打印当前区块链中的所有区块"""
        i = 1
        for block in self.blockChain.getChain():
            print('%s%s%s%s' % ('第', i, '个区块：', block))
            i += 1

    def listenForImput(self):
        """命令行函数"""
        waitingForInput = True

        while waitingForInput:
            print("帮助：")
            print("1：添加新的事务")
            print("2：挖掘新区块")
            print("3：打印所有区块")
            print("4：创建用户")
            print("5：加载用户")
            print('6：保存公私钥')
            print("q：退出")

            userChoice = input("请选择一项并执行：")

            # 命令行列表
            if userChoice == '1':
                txData = self.getTransactionValue()
                picUrl, phash = txData
                signature = self.user.signTransaction(self.user.publicKey, picUrl, phash)
                if self.blockChain.addTransaction(self.user.publicKey, picUrl, signature, phash):
                    print(self.blockChain.getOpenTransactions())
                else:
                    print('事务添加失败')
            elif userChoice == '2':
                if not self.blockChain.mineBlock:
                    print('挖掘失败，请检查是否存在已加载或创建的用户')
            elif userChoice == '3':
                self.printAllBlock()
            elif userChoice == '4':
                self.user.createKeys()
                self.blockChain = BlockChain(self.user.publicKey)
            elif userChoice == '5':
                self.user.loadKeys()
                self.blockChain = BlockChain(self.user.publicKey)
            elif userChoice == '6':
                self.user.saveKeys()
            elif userChoice == 'q':
                waitingForInput = False
            else:
                print("参数不合法，请重新输入")
                continue
            if not Verification.verifyChain(self.blockChain.getChain()):
                print("区块链不合法")
                waitingForInput = False


if __name__ == '__main__':
    node = Node()
    node.listenForImput()
