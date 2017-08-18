# coding=utf-8
from utils import invoke

import pytest
import sys

args = ['-s', '-q', '--alluredir', './Result']

Product=""

if __name__ == '__main__':
    if sys.argv[1] in ["chedunapp_dev","chedunapp","Mofang","Mofang_dev"]:
        Product = sys.argv[1]
    #args.append(sys.argv[1])
    pytest.main(args)
    cmd = 'allure generate %s -o %s' % ('./Result', './Result')
    try:
        invoke(cmd)
    except:
        print ("Html测试报告生成失败,确保已经安装了Allure-Commandline")

    # pytest -s -q --alluredir ./Result/report
    # allure generate Result/ -o Result/report
