# coding: utf-8
import requests
import json


import base64
import random
import math
import pytest
#测试环境说明
# 预挖持续块数 216
# 预挖解锁周期 14 块解锁 1/365
# 预挖时每块奖励 7013888888
# 普通时期每块奖励 1388888888
# 项目方解锁时间 1051块   每 432 块释放 1/24
# 团队解锁时间 1051块
import unittest
import time

token_addr = ""
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
    #print(response.text)
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
        res = request("invoke_contract", [account_addr, contract_addr, "on_deposit_asset", [param], asset_id, amount, 5000000, 1])
        return res
    else:
        res = request("transfer_to_contract",
                      [account_addr, contract_addr, "%.8f" % (float(amount) / 100000000),asset_id_tab[asset_id], "", "0.00000001", 500000,
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
        if a is None:
            init_simple_chain_env()
            generate_block()
    global token_addr
    if token_addr == "":
        nft_gpc_path = "erc721_forever_reward.glua.gpc"
        token_addr = deploy_contract(nft_gpc_path)

def balanceOf(account,owner):
    return int(invoke_contract_offline(account,token_addr,"balanceOf",owner)["result"]["api_result"])

def mint(account,tokenId):
    res = invoke_contract(account,token_addr,"mint","%s,%s,10"%(account,tokenId))
    return res["result"]["exec_succeed"]

def safeMint(account,tokenId):
    res = invoke_contract(account, token_addr, "safeMint", "%s,%s,10" % (account, tokenId))
    print(res)
    return res["result"]["exec_succeed"]

def transferFrom(account,_from,to,tokenId):
    print("%s,%s,%s"%(_from,to,tokenId))
    res = invoke_contract(account,token_addr,"transferFrom","%s,%s,%s"%(_from,to,tokenId))

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

def queryTokenMinter(account, tokenId):
    res = invoke_contract_offline(account,token_addr,"queryTokenMinter","%s"%tokenId)
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

class ERC721ForeverTest(unittest.TestCase):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        do_init()
        print(token_addr)
        invoke_contract("test", token_addr, "init_token", "WORLD,WORLD")
        generate_block()
        

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


    def test_mint(self):
        invoke_contract("test",token_addr,"mint","test,aaasssa,10")
        _all_test_tokens.append("aaasssa")
        generate_block()
        res = queryAllTokenIds("test")
        assert "aaasssa" in res
        minterStr = queryTokenMinter("test", "aaasssa")
        minter = json.loads(minterStr)
        assert minter["minter"] == "test"

    def test_mint2(self):
        invoke_contract("test", token_addr, "mint", "test,aaasssab,10")
        _all_test_tokens.append("aaasssab")
        generate_block()

        res = queryAllTokenIds("test")

        assert "aaasssab" in res


    def test_mint_trasfer_approve_loop(self):
        index = balanceOf("test","test")+1
        assert mint("test","yilixiaoshazi") == True
        _all_test_tokens.append("yilixiaoshazi")

        generate_block()
        res = tokenOfOwnerByIndex("test",index)
        assert res == "yilixiaoshazi"
        generate_block()
        res =ownerOf("test","yilixiaoshazi")
        assert res == "test"
        assert approve("test","test1","yilixiaoshazi")==True
        generate_block()
        assert getApproved("yilixiaoshazi") == "test1"
        test1_amount = balanceOf("test1","test1")
        print(balanceOf("test","test"))
        assert transferFrom("test1","test","test1","yilixiaoshazi") == True
        generate_block()
        _all_test_tokens.remove("yilixiaoshazi")
        assert self.check_test_token_match()
        assert test1_amount+1 == balanceOf("test1","test1")
        assert transferFrom("test1","test1","test","yilixiaoshazi") == True
        generate_block()
        _all_test_tokens.append("yilixiaoshazi")
        assert self.check_test_token_match()
        assert test1_amount == balanceOf("test1","test1")

    def test_mint_approve_all(self):
        assert mint("test", "yilixiaoshazi2") == True
        generate_block()
        _all_test_tokens.append("yilixiaoshazi2")
        assert setApprovalForAll("test","approve",True) == True
        generate_block()
        assert bool(isApprovedForAll("test","approve")) == True
        assert self.check_test_token_match()
        bak_list = []
        for i in range(len(_all_test_tokens)):
            data = _all_test_tokens.pop()
            bak_list.append(data)
            assert transferFrom("approve","test","approve",data)
            generate_block()
            assert self.check_test_token_match()
        for i in range(len(bak_list)):
            assert transferFrom("approve", "approve", "test", bak_list[i])
            generate_block()
            _all_test_tokens.append(bak_list[i])
            assert self.check_test_token_match()
        assert setApprovalForAll("test", "approve", False) == True
        generate_block()
        assert transferFrom("approve","test","approve","yilixiaoshazi2")==False

    def test_token_uri(self):
        for one_key in _all_test_tokens:
            res = invoke_contract_offline("test",token_addr,"tokenURI",one_key)
            print(res)

    def test_batch_mint(self):
        count = totalSupply()
        for i in range(1000):
            assert mint("test0%d"%i,"yilixiaoshazi_%d"%i)
            assert mint("test0%d" % i, "yilixiaoshazi_x_%d" % i)
            assert mint("test0%d" % i, "yilixiaoshazi_y_%d" % i)
            generate_block()
        assert  totalSupply() - count ==3000
        count = totalSupply()
        assert mint("test", "yilixiaoshazi3") == True
        generate_block()
        _all_test_tokens.append("yilixiaoshazi3")
        assert setApprovalForAll("test", "approve", True) == True
        generate_block()
        assert self.check_test_token_match()
        bak_list = []
        for i in range(len(_all_test_tokens)):
            data = _all_test_tokens.pop()
            bak_list.append(data)
            assert transferFrom("approve", "test", "approve", data)
            generate_block()
            assert self.check_test_token_match()
        for i in range(len(bak_list)):
            assert transferFrom("approve", "approve", "test", bak_list[i])
            generate_block()
            _all_test_tokens.append(bak_list[i])
            assert self.check_test_token_match()
        assert totalSupply() - count ==1

    def test_safeMint(self):
        res = deploy_contract("f:/work/code/xwc_nft/newtoken.glua.gpc")
        assert safeMint(res,"yilixiaoshazi-contract") ==False
        generate_block()
        assert safeMint("testsafe","yilixiaoshazi-contract") == True
        generate_block()
        tokens = queryAllTokenIds("testsafe")
        assert "yilixiaoshazi-contract" in tokens


    def test_safeTransferFrom(self):
        res = deploy_contract("f:/work/code/xwc_nft/newtoken.glua.gpc")
        assert safeMint(res, "yilixiaoshazi-safecontract") == False
        generate_block()
        assert safeMint("test", "yilixiaoshazi-safecontract") == True
        generate_block()
        assert safeTransferFrom("test","test",res,"yilixiaoshazi-safecontract") == False
        generate_block()
        assert safeTransferFrom("test","test","testsafe","yilixiaoshazi-safecontract") == True
        generate_block()
        assert "yilixiaoshazi-safecontract" in queryAllTokenIds("testsafe")

    def test_batch_token_index(self):
        res= totalSupply()
        data = set()
        for i in range(res):
            res = tokenByIndex(i)
            assert res not in data
            data.add(res)

    def test_offline_function(self):
        res = invoke_contract_offline("test",token_addr,"supportsERC721Interface","")
        print(res["result"]["api_result"])
        assert res["result"]["exec_succeed"]
        res = invoke_contract_offline("test",token_addr,"tokenName","")
        assert res["result"]["api_result"] == "WORLD"
        mint("testaaa","yilixiaoshazi_own")
        generate_block()
        res = invoke_contract_offline("test",token_addr,"ownerOf","yilixiaoshazi_own")
        assert res["result"]["api_result"] == "testaaa"
        res = invoke_contract_offline("test", token_addr, "symbol", "")
        assert res["result"]["api_result"] == "WORLD"





def suite():
    s = unittest.TestSuite()
    s.addTest(ERC721ForeverTest("test_mint"))
    s.addTest(ERC721ForeverTest("test_mint2"))
    s.addTest(ERC721ForeverTest("test_mint_trasfer_approve_loop"))
    s.addTest(ERC721ForeverTest("test_mint_approve_all"))
    s.addTest(ERC721ForeverTest("test_token_uri"))
    s.addTest(ERC721ForeverTest("test_safeTransferFrom"))
    s.addTest(ERC721ForeverTest("test_safeMint"))
    s.addTest(ERC721ForeverTest("test_batch_mint"))
    s.addTest(ERC721ForeverTest("test_offline_function"))
    return s


if __name__ == "__main__":
    s = suite()
    runner = unittest.TextTestRunner()
    runner.run(s)

    token_addr = ""
    swap_addr = ""
    swap_addr1 = ""
    hrc20_token_addr = ""
    swap_token_addr = ""
    current_block = 0

#     print(base64.b64encode(('%s:%s' % ("a", "b")).encode(encoding='utf-8')))





