# coding=utf-8
from config import product, chedunapp, Login_account
from InterfacePath import interface
from utils import sendRequest, get_sign, get_file_data, general_arg, general_case, compare
import pytest
import copy
import allure

path = product["chedunapp"]
url = interface["登录"]
constArg = copy.copy(chedunapp)

data = get_file_data('./Data/InterfaceTest1.xlsx')['Sheet1'][1:]


@pytest.fixture(scope="class")
def login():
    newPara = general_arg(constArg, Login_account)
    r = sendRequest(newPara, (path + url).strip())
    d=eval(r[0])["data"]
    return d["accessToken"]


@allure.testcase("用户注册")
class TestRegist:
    @pytest.mark.parametrize("url,param,expected", general_case("注册", data))
    @allure.feature('注册测试')
    def test_Regist(self, url, param, expected):
        newPara = general_arg(constArg, eval(param))
        r = sendRequest(newPara, (path + url).strip())
        assert compare(r[0], expected)


@allure.testcase("用户登录")
class Testlogin:
    @pytest.mark.parametrize("url,param,expected", general_case("登录", data))
    @allure.feature('登录测试')
    def test_others(self, url, param, expected):
        newPara = general_arg(constArg, eval(param))
        r = sendRequest(newPara, (path + url).strip())
        assert compare(r[0], expected)


@allure.testcase("查询车辆")
class TestGetVehicle:
    @pytest.mark.parametrize("url,param,expected", general_case("查询车辆", data))
    @allure.feature('查询车辆测试')
    def test_others(self, login,url, param, expected):
        newPara = general_arg(constArg, eval(param))
        r = sendRequest(newPara, (path + url).strip(),login)
        assert compare(r[0], expected)
