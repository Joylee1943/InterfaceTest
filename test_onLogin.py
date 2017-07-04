# coding=utf-8
from config import product
from InterfacePath import interface
from utils import sendRequest
import pytest
import hashlib

path=product["chedunapp"]
url=interface["登录"]

login_data=[({"account": "", "password": ""},{"code":10001,"data":"参数account错误！","msg":"参数错误！"}),({"account":"13701837591","password":""},{'code': 11004, 'data': '', 'msg': '密码错误！'})]

for data in login_data:
    m = hashlib.md5(data[0]["password"].encode("utf-8"))
    data[0]["password"]=m.hexdigest()

class Testlogin:
    @pytest.mark.parametrize("param,expected",login_data)
    def test_onLogin(self,param,expected):
        r = sendRequest(param,(path+url).strip())
        result=r[0]
        assert result==expected

