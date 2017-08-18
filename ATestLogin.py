# coding=utf-8
import hashlib
import MySQLdb
import xlrd, json, os, sys, re
import requests
from xlutils.copy import copy
import time
from datetime import datetime


def get_db():
    conn = MySQLdb.connect(host='192.168.8.203', user='acube_user', passwd='7W6/ftR1CEUYv61w', port=3306, db='acube',
                           charset='utf8')
    return conn


#从数据库中读取验证码
def get_verifyCode():
    time.sleep(20)
    try:
        conn = get_db()
        db = conn.cursor()
        # verifycode = "SELECT sms_content FROM t_sms_log where account='%s' ORDER BY update_time DESC LIMIT 1" % (
        #     ''.join(account.split()))
        verifycode = "SELECT sms_content FROM t_sms_log ORDER BY update_time DESC LIMIT 1"
        db.execute(verifycode)
        res = db.fetchall()
    except Exception as e:
        print(e)
        exit()
    return str(res[0])

#注册成功之后拿到用户的userId
def get_userId(account):
    try:
        conn = get_db()
        db = conn.cursor()
        userId = "SELECT id FROM t_user where account='%s'" % (''.join(account.split()))
        db.execute(userId)
        res = db.fetchall()
    except Exception as e:
        print(e)
        exit()
    return res[0]

#根据userId加notice数据，为了测试notice接口
def add_notice(userId):
    try:
        conn = get_db()
        db = conn.cursor()
        notice = "INSERT INTO t_notice(id,user_id,content,type,status) VALUES (1,%d,'test1',1,1), (2,%d,'test2',1,2), (3,%d,'test3',2,1)" % (
        userId, userId, userId)
        db.execute(notice)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        exit()
    # try:
    #     conn = get_db()
    #     db = conn.cursor()
    #     verifycode = "SELECT id FROM t_notice where user_id=%d"%userId
    #     db.execute(verifycode)
    #     res = db.fetchall()
    # except Exception as e:
    #     print(e)
    #     exit()
    # idList=[]
    # for id in res[0]:
    #     idList.append(id)
    # return idList


def delete_user():
    try:
        conn = get_db()
        db = conn.cursor()
        user = "delete from t_user where account='13701837591'"
        db.execute(user)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        exit()


def delete_vehicle():
    try:
        conn = get_db()
        db = conn.cursor()
        vehicle = "DELETE FROM t_user_vehicle where vehicle_SN='LSGGA54Y6CH224814'"
        db.execute(vehicle)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        exit()

def clean_testdata():
    try:
        conn = get_db()
        db = conn.cursor()
        user = "delete from t_user where account='13701837591'"
        db.execute(user)
        vehicle = "DELETE FROM t_user_vehicle where vehicle_SN='LSGGA54Y6CH224814' or vehicle_SN='LSGGF53W4BH313183'"
        db.execute(vehicle)
        notice = "DELETE from t_notice where id in (1,2,3)"
        db.execute(notice)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        exit()


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


# 开始时间
oldwb = xlrd.open_workbook(r'./Data/InterfaceTest.xlsx')
oldsh = oldwb.sheet_by_index(0)
nrows = oldsh.nrows
newwb = copy(oldwb)
newsh = newwb.get_sheet(0)


if __name__ == '__main__':
    # 删除已存在的测试账户13701837591
    #删除已存在的测试车辆LSGGA54Y6CH224814
    #如果有notice也删除
    clean_testdata()
    #备用user 33，如果注册接口失败，就用33去跑其他case
    userId = 33
    #固定notice，id为1,2,3
    add_notice(userId)

    for i in range(1, nrows):
        arg = oldsh.cell_value(i, 1)
        url = oldsh.cell_value(i, 2)
        arg1 = eval(arg)
        #userId = 33
        if ("password" in arg1):
            m = hashlib.md5(arg1["password"].encode("utf-8"))
            arg1["password"] = m.hexdigest()
        #如果verifyCode在参数列表，并且标记为1，则读取数据库中的验证码
        if ("verifyCode" in arg1 and arg1["verifyCode"] == '1'):
            arg1["verifyCode"] = (re.sub("\D","",get_verifyCode()))[:6]
        if ("userId" in arg1 and arg1["userId"] == 2):
            arg1["userId"] = userId
        r = sendRequest(arg1, "http://dev.a-cube.cn/app_server/" + url.strip())

        try:
            newsh.write(i, 4, str(r[0]))
            newsh.write(i, 6, datetime.now().strftime('%Y-%m-%d-%H%M%S'))
            newsh.write(i, 7, r[1])
            # ar=(oldsh.cell(i,4).value).strip(' \'\"')
            er = oldsh.cell(i, 3).value
            if (er != ''):
                d2 = dict(eval(er))
                if str(r[0]) == str(d2):
                    newsh.write(i, 5, "pass")
                else:
                    newsh.write(i, 5, "fail")
            else:
                #if ('userId' in r[0]["data"] and r[0]["code"] == 0):
                if (r[0]["code"] == 0 and r[0]["msg"]=="成功"):
                    newsh.write(i, 5, "pass")
                    #userId = r[0]["data"]["userId"]
        except Exception as e:
            newsh.write(i, 5, "发送请求异常")

        print("第%d case执行完毕" % i)

    result_file = "{0}/接口测试{1}.xls".format('./Result', datetime.now().strftime('%Y-%m-%d-%H%M%S'))
    newwb.save(result_file)
