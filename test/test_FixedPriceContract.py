# coding: utf-8
import requests
import json


import base64
import random
import math
import unittest
import time

token_addr = ""
ex_addr = ""
_all_test_tokens = []
current_block = 0
is_simplechain = True
def request(method,params):
    global is_simplechain
    if is_simplechain:
        url = "http://127.0.0.1:8080/api"
    else:
        url = "http://127.0.0.1:19998/api"

    payload = "{\"jsonrpc\": \"2.0\",\r\n    \"params\": [],\r\n    \"id\": \"45\",\r\n    \"method\": \"" + method + "\"\r\n    }"
    headers = {
        'content-type': "application/json",
        'authorization': "Basic YTpi"
    }

    user = 'a'
    passwd = 'b'
    basestr = base64.b64encode(('%s:%s' % (user, passwd)).encode("utf-8"))
    args_j = json.dumps(params)
    payload = "{\r\n \"id\": 1,\r\n \"method\": \"%s\",\r\n \"params\": %s\r\n}" % (method, args_j)
    headers = {
        'content-type': "text/plain",
        'authorization': "Basic %s" % (basestr),
        'cache-control': "no-cache",
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    # print(response.text)
    return json.loads(response.text)

# 初始化simplechain 测试环境
def init_simple_chain_env():
    request("add_asset", ["XWC", 8])
    request("add_asset",["ETH",8])
    request("mint",["test",1,50000000000000000])
    request("mint", ["test",2, 50000000000000000])
    request("mint", ["test1", 1, 50000000000000000])
    request("mint", ["test1", 2, 50000000000000000])


# 产块
def generate_block():
    global current_block
    current_block +=1
    if is_simplechain:
        request("generate_block",[])
    else:
        time.sleep(10)

#产10个块
def generate_block_10():
    global current_block
    current_block += 10
    if is_simplechain:

        res = request("generate_block", [10])
        print("generate10 ",res)
    else:
        time.sleep(50)

def deploy_contract(contractFile):
    import os
    gpcPath = os.path.abspath(os.path.join(os.getcwd(), ".."))
    contractPath = os.path.abspath(os.path.join(gpcPath, contractFile))
    if is_simplechain:
        res = request("create_contract_from_file",["test",contractPath,1000000,10000])
        generate_block()
        print("deploy_contract",res["result"])
        return res["result"]["contract_address"]
    else:
        res = request("register_contract", ["test", "0.00001", 500000, contractPath])
        print(res["result"]["contract_id"])
        generate_block()
        return res["result"]["contract_id"]


def invoke_contract(account_name,contract_addr,method,params):
    if is_simplechain:
        res = request("invoke_contract",
                      [account_name, contract_addr, method, [params], 0, 0, 5000000, 1])
        if account_name == "test":
            print("method:"+method+"  res: ",res)
        return res
    else:
        res = request("invoke_contract",
                      [account_name, "0.00001", 500000, contract_addr, method, params])
        print("method:" + method + "  res: ", res)
        return res


def invoke_contract_offline(account_name,contract_addr,method,params):
    if is_simplechain:
        res = request("invoke_contract_offline", [account_name, contract_addr, method, [params], 0, 0])
        print("offline method:" + method + "  res: ", res)
        return res
    else:
        res = request("invoke_contract_offline", [account_name, contract_addr, method, params])
        print("offline method:" + method + "  res: ", res)
        return res


def deposit_contract(account_addr,contract_addr,param,asset_id=0,amount=0):
    if is_simplechain:
        res = request("invoke_contract", [account_addr, contract_addr, "on_deposit_asset", [param], amount, asset_id, 5000000, 1])
        return res
    else:
        res = request("transfer_to_contract",
                        [account_addr, contract_addr, "%.8f" % (float(amount) / 100000000), asset_id, param, "0.00000001", 500000,
                        "true"])
    return res

def getStorage(contract_addr,storage_name):
    res = request("get_storage", [contract_addr, storage_name])["result"]
    return res

def query_native_balance(account_name="test"):
    res= request("get_account_balances",[account_name])
    return res

def do_init():
    if is_simplechain:
        a = query_native_balance("test")
        if a is None or a == 0:
            init_simple_chain_env()
            generate_block()
    global token_addr
    global ex_addr
    if token_addr == "":
        token_addr = deploy_contract("erc721_forever_reward.glua.gpc")
    print(token_addr)
    if ex_addr == "":
        ex_addr = deploy_contract("fixedPriceContract.glua.gpc")


def balanceOf(account,owner):
    return int(invoke_contract_offline(account,token_addr,"balanceOf",owner)["result"]["api_result"])

def mint(account, tokenId, feeRate=10):
    res = invoke_contract(account,token_addr,"mint","%s,%s,%s"%(account,tokenId,feeRate))
    return res["result"]["exec_succeed"]

def safeMint(account,tokenId):
    res = invoke_contract(account, token_addr, "safeMint", "%s,%s,10" % (account, tokenId))
    print(res)
    return res["result"]["exec_succeed"]

def transferFrom(account,_from,to,tokenId):
    print("%s,%s,%s"%(_from,to,tokenId))
    res = invoke_contract(account,token_addr,"transferFrom","%s,%s,%s"%(_from,to,tokenId))
    print(res)
    return res["result"]["exec_succeed"]

def safeTransferFrom(account,_from,to,tokenId):
    print("%s,%s,%s"%(_from,to,tokenId))
    res = invoke_contract(account,token_addr,"safeTransferFrom","%s,%s,%s"%(_from,to,tokenId))

    return res["result"]["exec_succeed"]

def tokenOfOwnerByIndex(account,index):
    res = invoke_contract_offline(account,token_addr,"tokenOfOwnerByIndex","%s,%s"%(account,index))
    return res["result"]["api_result"]

def approve(account,to,tokenId):
    res = invoke_contract(account, token_addr, "approve", "%s,%s"%(to,tokenId))
    return res["result"]["exec_succeed"]

def ownerOf(account,tokenId):
    res = invoke_contract_offline(account,token_addr,"ownerOf","%s"%tokenId)
    return res["result"]["api_result"]

def setApprovalForAll(account,operator,open):
    openStr =  "true" if open else "false"
    print(openStr)
    res = invoke_contract(account,token_addr,"setApprovalForAll","%s,%s"%(operator,openStr))
    return res["result"]["exec_succeed"]

def queryAllTokenIds(account):
    amount = balanceOf(account,account)
    tokens =[]
    print("queryAllTokenIds",amount)
    for i in range(amount):
        res = tokenOfOwnerByIndex(account,i+1)
        tokens.append(res)
    return tokens

def transfer(account,amount):
    res = request("transfer",["test",account,amount,"XWC","","true"])
    print(res)

def totalSupply():
    res = invoke_contract_offline("test",token_addr,"totalSupply","")
    return int(res["result"]["api_result"])

def tokenByIndex(index):
    res = invoke_contract_offline("test",token_addr,"tokenByIndex","%d"%index)
    return res["result"]["api_result"]

def getApproved(tokenId):
    res = invoke_contract_offline("test",token_addr,"getApproved",tokenId)
    return res["result"]["api_result"]

def isApprovedForAll(owner,spender):
    res = invoke_contract_offline("test", token_addr, "isApprovedForAll", "%s,%s"%(owner,spender))
    print("isApprovedForAll",res)
    return res["result"]["api_result"]

class FixedPriceTest(unittest.TestCase):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        do_init()
        invoke_contract("test", token_addr, "init_token", "WORLD,WORLD")
        generate_block()
        invoke_contract("test", token_addr, "setFixedSellContract", ex_addr)
        generate_block()
        self.token2Id = {
            "XWC": 1,
            "ETH": 2
        }

    def check_test_token_match(self):
        tokens = queryAllTokenIds("test")
        if len(tokens) == len(_all_test_tokens):

            for one_key in tokens:
                if one_key not in _all_test_tokens:
                    print("check_test_token_match", tokens, _all_test_tokens)
                    return False
            return True
        else:
            print("check_test_token_match", tokens, _all_test_tokens)
            return  False

    def trade_base(self, tokenAddr, tokenId, price, symbol):
        res = invoke_contract_offline("test", ex_addr, "getInfo", "")
        infoStart = json.loads(res['result']['api_result'])
        if isinstance(infoStart['totalReward'],list):
            infoStart['totalReward'] = {}
            infoStart['totalReward'][symbol] = 0
            infoStart['currentReward'] = {}
            infoStart['currentReward'][symbol] = 0
        elif symbol not in infoStart['totalReward']:
            infoStart['totalReward'][symbol] = 0
            infoStart['currentReward'][symbol] = 0            
        assert mint("test", tokenId) == True
        generate_block()
        owner = invoke_contract_offline("test", token_addr, "ownerOf", tokenId)
        assert owner["result"]["api_result"] == "test"
        assert approve("test", ex_addr, tokenId) == True
        generate_block()
        assert getApproved(tokenId) == ex_addr
        invoke_contract("test", ex_addr, "sellNft", f"{tokenId},{tokenAddr},{price},{symbol}")
        generate_block()
        owner = invoke_contract_offline("test", tokenAddr, "ownerOf", tokenId)
        assert owner["result"]["api_result"] == ex_addr
        tokenInfoStr = invoke_contract_offline("test", ex_addr, "getTokenInfo", f"{tokenAddr},{tokenId}")
        tokenInfo = json.loads(tokenInfoStr["result"]["api_result"])
        assert tokenInfo["price"] == f"{price}"
        deposit_contract("test1", ex_addr, f"{tokenAddr},{tokenId}", price, self.token2Id[symbol])
        generate_block()
        res = invoke_contract_offline("test", ex_addr, "getInfo", "")
        infoEnd = json.loads(res['result']['api_result'])
        print(infoEnd)
        print(infoEnd["totalReward"][symbol])
        assert infoEnd["totalReward"][symbol] == int(price * infoStart["feeRate"] / 100) + infoStart["totalReward"][symbol]
        assert infoEnd["currentReward"][symbol] == int(price * infoStart["feeRate"] / 100) + infoStart["currentReward"][symbol]
        invoke_contract("test", ex_addr, "withdrawReward", f"1,{symbol}")
        generate_block()
        res = invoke_contract_offline("test", ex_addr, "getInfo", "")
        infoLast = json.loads(res['result']['api_result'])
        assert infoLast["totalReward"][symbol] == infoEnd["totalReward"][symbol]
        assert infoLast["currentReward"][symbol] == infoEnd["currentReward"][symbol] - 1

    def test_normalTrade(self):
        self.trade_base(token_addr, "token1", 10000000, "XWC")
        self.trade_base(token_addr, "token2", 100, "ETH")

    def  test_errorSymbolTrade(self):
        tokenId = "error1"
        price = 10000
        symbol = 'XWC'
        assert mint("test", tokenId) == True
        generate_block()
        assert approve("test", ex_addr, tokenId) == True
        generate_block()
        invoke_contract("test", ex_addr, "sellNft", f"{tokenId},{token_addr},{price},{symbol}")
        generate_block()
        res = deposit_contract("test1", ex_addr, f"{token_addr},{tokenId}", price, 2)
        assert res['result']['error'] == "token sell in different symbol"

    def test_setFeeRate(self):
        res = invoke_contract("test", ex_addr, "setFeeRate", "-1")
        assert res['result']['error'] == 'invalid fee rate: -1'
        res = invoke_contract("test", ex_addr, "setFeeRate", "0")
        assert res['result']['exec_succeed'] == True
        res = invoke_contract("test", ex_addr, "setFeeRate", "50")
        assert res['result']['exec_succeed'] == True
        res = invoke_contract("test", ex_addr, "setFeeRate", "51")
        assert res['result']['error'] == 'invalid fee rate: 51'

    def test_changeSellParam(self):
        tokenId = "tobechanged"
        self.assertEqual(mint("test", tokenId), True)
        generate_block()
        self.assertEqual(approve("test", ex_addr, tokenId), True)
        generate_block()
        invoke_contract("test", ex_addr, "sellNft", f"{tokenId},{token_addr},10000,XWC")
        generate_block()
        invoke_contract("test", ex_addr, "changeSellParam", f"{tokenId},{token_addr},20000,ETH")
        generate_block()
        tokenInfoStr = invoke_contract_offline("test", ex_addr, "getTokenInfo", f"{token_addr},{tokenId}")
        tokenInfo = json.loads(tokenInfoStr["result"]["api_result"])
        self.assertEqual(tokenInfo["price"], "20000")
        self.assertEqual(tokenInfo["symbol"], "ETH")
        invoke_contract("test1", ex_addr, "changeSellParam", f"{tokenId},{token_addr},30000,XWC")
        generate_block()
        tokenInfoStr = invoke_contract_offline("test", ex_addr, "getTokenInfo", f"{token_addr},{tokenId}")
        tokenInfo = json.loads(tokenInfoStr["result"]["api_result"])
        self.assertEqual(tokenInfo["price"], "20000")
        self.assertEqual(tokenInfo["symbol"], "ETH")

    def test_revokeSellNft(self):
        tokenId = "toberevoked"
        self.assertEqual(mint("test", tokenId), True)
        generate_block()
        self.assertEqual(approve("test", ex_addr, tokenId), True)
        generate_block()
        invoke_contract("test", ex_addr, "sellNft", f"{tokenId},{token_addr},10000,XWC")
        generate_block()
        tokenListStr = invoke_contract_offline("test", ex_addr, "getSellList", "")
        tokenList = json.loads(tokenListStr['result']['api_result'])
        tokenLen = len(tokenList)
        self.assertEqual(f"{token_addr}.{tokenId}" in tokenList, True)
        invoke_contract("test", ex_addr, "revokeSellNft", f"{tokenId},{token_addr}")
        generate_block()
        tokenInfoStr = invoke_contract_offline("test", ex_addr, "getTokenInfo", f"{token_addr},{tokenId}")
        tokenInfo = json.loads(tokenInfoStr["result"]["api_result"])
        self.assertEqual("price" in tokenInfo, False)
        tokenListStr = invoke_contract_offline("test", ex_addr, "getSellList", "")
        tokenList = json.loads(tokenListStr['result']['api_result'])
        self.assertEqual(len(tokenList), tokenLen-1)



def suite():
    s = unittest.TestSuite()
    s.addTest(FixedPriceTest("test_normalTrade"))
    s.addTest(FixedPriceTest("test_errorSymbolTrade"))
    s.addTest(FixedPriceTest("test_setFeeRate"))
    s.addTest(FixedPriceTest("test_changeSellParam"))
    s.addTest(FixedPriceTest("test_revokeSellNft"))
    return s


if __name__ == "__main__":
    s = suite()
    runner = unittest.TextTestRunner()
    runner.run(s)
    token_addr = ""
    current_block = 0





