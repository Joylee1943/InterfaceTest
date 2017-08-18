# coding=utf-8
import csv
import hashlib
import json
import os
from datetime import time
import time
import subprocess

import MySQLdb
import allure
import requests
import xlrd
import xlwt
from collections import Iterable


def get_db():
    conn = MySQLdb.connect(host='192.168.8.203', user='acube_user', passwd='7W6/ftR1CEUYv61w', port=3306, db='acube',
                           charset='utf8')
    return conn


def invoke(cmd):
    # shell设为true，程序将通过shell来执行
    # stdin, stdout, stderr分别表示程序的标准输入、输出、错误句柄。
    # 他们可以是PIPE，文件描述符或文件对象，也可以设置为None，表示从父进程继承。
    # subprocess.PIPE实际上为文本流提供一个缓存区
    output, errors = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    o = output.decode("utf-8")
    return o


def write_excel_data(data, excel, overwrite=False):
    if not data:
        print(data)
        return False
    if os.path.isfile(excel) and not overwrite:
        print('发现【%s】文件已存在，是否覆盖(yes/no)？' % excel),
        overwrite = str.lower(input())
        if overwrite != 'yes' and overwrite != 'y':
            print('程序已退出')
            return False
    print('开始写入数据...', end="")

    workbook = xlwt.Workbook(encoding='utf-8')
    if isinstance(data, dict):
        for sheetname in sorted(data.keys()):
            sheetdata = data[sheetname]
            sheet = workbook.add_sheet(sheetname, cell_overwrite_ok=True)
            for row in range(len(sheetdata)):
                rowdata = sheetdata[row]
                for col in range(len(rowdata)):
                    content = rowdata[col]
                    sheet.write(row, col, str(content))
    elif isinstance(data, (list, Iterable)):
        sheet = workbook.add_sheet(u'Sheet1', cell_overwrite_ok=True)
        for row, rowdata in enumerate(data):
            if isinstance(rowdata, (list, tuple)):
                for col, coldata in enumerate(rowdata):
                    sheet.write(row, col, str(coldata))
            else:
                sheet.write(row, 0, str(rowdata))
    else:
        print("数据格式错误")

    try:
        workbook.save(excel)
        print('完成，结果文件:  %s' % excel)
        return True
    except Exception as e:
        print(e)
        return False


def get_file_data(file):
    ext = os.path.splitext(file)[1]
    if ext == ".csv":
        return get_csv_data(file)
    elif ext in [".xls", ".xlsx"]:
        return get_excel_data(file)


def get_csv_data(file):
    if not os.path.isfile(file):
        print('%s 文件不存在' % file)
        return False
    else:
        print('开始读取数据...', end="")
    with open(file, "r", encoding="utf-8") as csvfile:
        rd = csv.reader(csvfile)
        print("完成")
        return [l for l in rd]


def get_excel_data(excel):
    if not os.path.isfile(excel):
        print('%s 文件不存在' % excel)
        return False
    else:
        print('开始读取数据...', end="")

    workbook = xlrd.open_workbook(excel, encoding_override="utf-8")
    worksheets = workbook.sheets()
    data = dict()
    for sheet in worksheets:
        sheet_data = []
        for row in range(sheet.nrows):
            row_data = []
            for col in range(sheet.ncols):
                if sheet.cell(row, col).ctype == xlrd.XL_CELL_DATE:
                    value = xlrd.xldate.xldate_as_datetime(sheet.cell(row, col).value, 0)
                else:
                    value = sheet.cell(row, col).value
                row_data.append(value)
            sheet_data.append(row_data)
        data[sheet.name] = sheet_data
    print('完成')
    return data


@allure.step("生成sign值")
def get_sign(args, product):
    result = []
    for keys, values in args.items():
        # print(values)
        if not isinstance(values, str):
            values = str(values)
        result.append(values)

    if product in ["chedunapp_dev", "chedunapp"]:
        result.append("9a93a8b14d664f2e")
    elif product in ["mofang_dev", "mofang"]:
        result.append("6613787ce111640e9b43")

    result.sort()
    # print("排序之后的数据：", result)
    result_join = '&'.join(result)
    # print("拼接之后的数据：", result_join)

    m = hashlib.md5(result_join.encode("utf-8"))
    print(m.hexdigest())
    return m.hexdigest()


@allure.step("发送request")
def sendRequest(arg, url, token=''):
    print(arg)
    print(url)
    try:
        if token == '':
            headers = {"content-type": "application/json"}
        else:
            headers = {"content-type": "application/json", "Authorization": token}
        Start = time.time()
        r = requests.post(url, data=json.dumps(arg), headers=headers)
        End = time.time()
        diff = End - Start
        return r.content.decode(), diff
    except Exception as e:
        print(e)


@allure.step("生成参数")
def general_arg(const_arg, param, product):
    if "password" in param:
        m = hashlib.md5(param["password"].encode("utf-8"))
        param["password"] = m.hexdigest()

    newParam = dict(const_arg, **param)
    newParam["sign"] = get_sign(newParam, product)

    if product in ["chedunapp_dev", "chedunapp"]:
        return newParam
    elif product in ["mofang_dev", "mofang"]:
        #print("requestJSON=" + newParam)
        return newParam


@allure.step("获取{0} case")
def general_case(tag, product):
    data = []
    if product in ["chedunapp_dev", "chedunapp"]:
        data = get_file_data('./Data/ChedunApp_InterfaceTest.xlsx')['Sheet1'][1:]
    elif product in ["mofang_dev", "mofang"]:
        data = get_file_data('./Data/Mofang_InterfaceTest.xlsx')['Sheet1'][1:]

    case_list = []
    for d in data:
        if d[0] == tag:
            case_list.append(d[1:])

    return case_list


@allure.step("对比结果")
def compare(ac, ex):
    actual = eval(ac)
    expected = eval(ex)
    if "code" in actual and actual["code"] != expected["code"]:
        return False

    if "errorCode" in actual and actual["errorCode"] != expected["code"]:
        return False

    if "msg" in actual and actual["msg"] != expected["msg"]:
        return False

    return True
