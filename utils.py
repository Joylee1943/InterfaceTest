# coding=utf-8
import hashlib
import json
import os
from datetime import time
import time
import subprocess

import MySQLdb
import requests
import xlwt
from collections import Iterable


def get_sign(dict={}):
    result = []
    for keys, values in dict.items():
        # print(values)
        result.append(values)
    # key=6613787ce111640e9b43
    result.append("6613787ce111640e9b43")
    result.sort()

    result_join = '&'.join(result)

    m = hashlib.md5(result_join.encode("utf-8"))
    return m.hexdigest()

def sendRequest(arg, url):
    try:
        headers = {"content-type": "application/json"}
        Start = time.time()
        # eval 将字符串str当成有效的表达式来求值并返回计算结果。
        r = requests.post(url, data=json.dumps(arg), headers=headers)
        End = time.time()
        diff = End - Start
        results = r.json()
        return results, diff
    except Exception as e:
        print(e)


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
