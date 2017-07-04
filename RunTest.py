# coding=utf-8
from utils import invoke

import pytest
import sys

args = ['-s', '-q', '--alluredir', './Result']
#Product = "Mofang"
if __name__ == '__main__':
    # if sys.args[4] == "CheDunDev":
    #     Product = "CheDunDev"
    pytest.main(args)
    cmd = 'allure generate %s -o %s' % ('./Result', './Result')
    try:
        invoke(cmd)
    except:
        print ("Html测试报告生成失败,确保已经安装了Allure-Commandline")

    # pytest -s -q --alluredir ./Result/report
    # allure generate Result/ -o Result/report
