# coding=utf-8
import hashlib as hl
import json


def hashString256(string):
    return hl.sha256(string).hexdigest()


def hashBlock(block):

    """返回区块的哈希字符串"""
    hashableBlock = block.__dict__.copy()
    hashableBlock['transactions'] = [tx.toOrderedDict() for tx in hashableBlock['transactions']]
    return hashString256(json.dumps(hashableBlock, sort_keys=True).encode())
