# coding=utf-8
from collections import OrderedDict
from utility.printable import Printable


class Transaction(Printable):
    def __init__(self, copyrightOwner, picUrl, signature, picPhash):
        self.copyrightOwner = copyrightOwner
        self.picUrl = picUrl
        self.picPhash = picPhash
        self.signature = signature

    def toOrderedDict(self):
        return OrderedDict([
            ('copirightOwner', self.copyrightOwner.encode('utf-8')),
            ('picUrl', self.picUrl.encode('utf-8')),
            ('picPhash', self.picPhash.encode('utf-8'))])

    # def printTransactions(self):
    #     print(
    #         '%s%s%s%s%s%s%s'%
    #         ('\t\tcopyrightOwner:',self.copyrightOwner,
    #          '\n\t\tpicUrl:',self.picUrl,
    #          '\n\t\tpicPhash:',self.picPhash,'\n')
    #     )
