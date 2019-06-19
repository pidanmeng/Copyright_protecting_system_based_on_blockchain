# coding=utf-8
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from users import Users
from utility.DHash import DHash, url_to_image
from blockChain import BlockChain

app = Flask(__name__)
CORS(app)


@app.route('/user', methods=['POST'])
def createKeys():
    user.createKeys()
    if user.saveKeys():
        global blockChain
        blockChain = BlockChain(user.publicKey, port)
        response = {
            'message': '创建私钥成功',
            'publicKey': user.publicKey,
            'privateKey': user.privateKey,
            'copyright': blockChain.getCopyrightInfo()
        }
        return jsonify(response), 201
    else:
        response = {'message:''保存私钥失败'}
        return jsonify(response), 500


@app.route('/user', methods=['GET'])
def loadKeys():
    if user.loadKeys():
        global blockChain
        blockChain = BlockChain(user.publicKey, port)
        response = {
            'message': '加载私钥成功',
            'publicKey': user.publicKey,
            'privateKey': user.privateKey,
            'copyright': blockChain.getCopyrightInfo()
        }
        return jsonify(response), 201
    else:
        response = {'message': '加载私钥失败'}
        return jsonify(response), 500


@app.route('/copyright', methods=['GET'])
def getCopyrightInfo():
    copyright = blockChain.getCopyrightInfo()
    if copyright is not None:
        response = {
            'message': '加载版权信息成功',
            'copyrightInfo': copyright
        }
        return jsonify(response), 201
    else:
        response = {
            'message': '加载版权信息失败',
            'userSetUp': user.publicKey is not None
        }
        return jsonify(response), 500


@app.route('/', methods=['GET'])
def getUi():
    return render_template("node.html", object='BlockChain')


@app.route('/broadcastTransaction', methods=['POST'])
def broadcastTransaction():
    values = request.get_json(force=True)
    source = request.host
    print source
    if not values:
        response = {'message': '被广播的事务不存在或解析异常'}
        return jsonify(response), 400
    required = ['copyrightOwner', 'picUrl', 'picPhash', 'signature']
    if not all(key in values for key in required):
        response = {'message': '被广播图片事务数据不完整'}
        return jsonify(response), 400
    success = blockChain.addTransaction(
        values['copyrightOwner'], values['picUrl'], values['signature'], values['picPhash'], isReceiving=True)
    if success:
        response = {
            'message': '被广播图片事务添加成功',
            'transaction': {
                'copyrightOwner': values['copyrightOwner'],
                'picUrl': values['picUrl'],
                'picPhash': values['picPhash'],
                'signature': values['signature']
            },
        }
        return jsonify(response), 201
    else:
        response = {'message': '被广播事务添加失败'}
        return jsonify(response), 500


@app.route('/broadcastBlock', methods=['POST'])
def broadcastBlock():
    values = request.get_json(force=True)
    if not values:
        response = {'message': '被广播的区块不存在或解析异常'}
        return jsonify(response), 400
    if 'block' not in values:
        response = {'message': '被广播区块的数据不完整'}
        return jsonify(response), 400
    block = values['block']
    if block['index'] == blockChain.chain[-1].index + 1:
        print(block['index'])
        print(blockChain.chain[-1].index + 1)
        if blockChain.addBlock(block):
            response = {'message': '被广播的区块已更新上链'}
            return jsonify(response), 201
        else:
            response = {'message': '被广播的区块不合法,上链失败'}
            return jsonify(response), 409
    elif block['index'] > blockChain.chain[-1].index:
        response = {'message': '区块链长度与被广播的区块链不匹配,本地区块链较短,需要更新'}
        blockChain.resolveConflicts = True
        return jsonify(response), 200
    else:
        response = {'message': '区块链长度与被广播的区块链不匹配,本地区块链较长,无需上链'}
        return jsonify(response), 409


@app.route('/tort', methods=['POST'])
def isTort():
    values = request.get_json(force=True)
    if not values:
        response = {'message': '数据不存在或解析异常'}
        return jsonify(response), 400
    if 'urls' not in values:
        response = {'message': '数据不完整'}
        return jsonify(response), 400
    urls = values['urls']
    tort = []
    notTort = []
    notImg = []
    for url in urls:
        try:
            picPhash = DHash.calculate_hash(url_to_image(url))
            if blockChain.isPhashInChain(picPhash):
                tort.append(url)
            else:
                notTort.append(url)
        except ValueError:
            notImg.append(url)

    if not (len(tort) or len(notTort) or len(notImg)):
        response = {'message': '无数据'}
        return jsonify(response), 400
    try:
        response = {
            'message': '侵权判定结束',
            'tort': tort,
            'notTort': notTort,
            'notImg': notImg
        }
        return jsonify(response), 200
    except ValueError:
        response = {
            'message': '侵权判定失败'
        }
        return jsonify(response), 500


@app.route('/transaction', methods=['POST'])
def addTransaction():
    if user.publicKey is None:
        response = {'message': '未设定用户'}
        return jsonify(response), 400
    values = request.get_json(force=True)
    print (type(request.get_json(force=True)))
    if not values:
        response = {'message': '事务列表不存在或数据解析异常'}
        return jsonify(response), 400
    requiredFields = ['picUrl']
    if not all(field in values for field in requiredFields):
        response = {'message': '数据不完整'}
        return jsonify(response), 400
    picUrl = values['picUrl']
    try:
        picPhash = DHash.calculate_hash(url_to_image(values['picUrl']))
    except ValueError:
        response = {'message': 'url指向非图片资源或格式不正确'}
        return jsonify(response), 400
    signature = user.signTransaction(user.publicKey, picUrl, picPhash)
    success = blockChain.addTransaction(user.publicKey, picUrl, signature, picPhash)
    if success:
        response = {
            'message': '添加新事务成功!',
            'transaction': {
                'copyrightOwner': user.publicKey,
                'picUrl': picUrl,
                'picPhash': picPhash,
                'signature': signature
            },
            'copyright': blockChain.getCopyrightInfo()
        }
        return jsonify(response), 201
    else:
        response = {'message': '添加新事务失败,原因可能是数字签名验证不通过或链上有相同的图片'}
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
    if blockChain.resolveConflicts:
        response = {'message': '区块链可能需要被更新'}
        return jsonify(response), 409
    block = blockChain.mineBlock
    if block is not None:
        dictBlock = block.__dict__.copy()
        dictBlock['transactions'] = [tx.__dict__ for tx in dictBlock['transactions']]
        response = {
            'message': '挖矿成功',
            'block': dictBlock,
            'copyrightInfo': blockChain.getCopyrightInfo()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': '挖矿失败',
            'userSetUp': bool(user.publicKey)
        }
        return jsonify(response), 500


@app.route('/resolveConflicts', methods=['POST'])
def resolveConflicts():
    replaced = blockChain.resolve()
    if replaced:
        response = {'message': '区块链已被更新'}
    else:
        response = {'message': '区块链足够长故未被更新'}
    return jsonify(response), 200


@app.route('/transactions', methods=['GET'])
def getOpenTransaction():
    transactions = blockChain.getOpenTransactions()
    dictTransactions = [tx.__dict__ for tx in transactions]
    response = {
        'message': '成功获取事务列表',
        'transactions': dictTransactions
    }
    return jsonify(response), 200


@app.route('/chain', methods=["GET"])
def getChain():
    chainSnapshot = blockChain.chain
    dictChain = [block.__dict__.copy() for block in chainSnapshot]
    for dictBlock in dictChain:
        dictBlock['transactions'] = [tx.__dict__ for tx in dictBlock['transactions']]
    return jsonify(dictChain), 200


@app.route('/node', methods=['POST'])
def addNode():
    values = request.get_json(force=True)
    if not values:
        response = {
            'message': '无数据或数据解析异常'
        }
        return jsonify(response), 400
    if 'node' not in values:
        response = {
            'message': '无结点数据'
        }
        return jsonify(response), 400
    node = values['node']
    blockChain.addPeerNode(node)
    response = {
        'message': '添加结点成功',
        'allNodes': blockChain.getPeerNodes()
    }
    return jsonify(response), 201


@app.route('/node/<nodeUrl>', methods=['DELETE'])
def removeNode(nodeUrl):
    if nodeUrl == '' or nodeUrl is None:
        response = {'message': '无数据'}
        return jsonify(response), 400
    blockChain.removePeerNode(nodeUrl)
    response = {
        'message': '删除结点成功',
        'allNodes': blockChain.getPeerNodes()
    }
    return jsonify(response), 201


@app.route('/node', methods=['GET'])
def getNodes():
    response = {'allNodes': blockChain.getPeerNodes()}
    return jsonify(response), 201


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int)
    args = parser.parse_args()
    port = args.port
    user = Users(port)
    blockChain = BlockChain(user.publicKey, port)
    app.run(host='localhost', port=port)
