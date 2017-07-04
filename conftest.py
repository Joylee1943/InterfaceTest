# coding=utf-8
import pytest
from utils import get_db

@pytest.fixture()
def setup(request):
    try:
        conn = get_db()
        db = conn.cursor()
        user="INSERT INTO t_user(id,account,password) VALUES (0,'13701837591','dc483e80a7a0bd9ef71d8cf973673924')"
        db.execute(user)
        notice = "INSERT INTO t_notice(id,user_id,content,type,status) VALUES (1,0,'test1',1,1), (2,0,'test2',1,2), (3,0,'test3',2,1)"
        db.execute(notice)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
    def fin():
        try:
            conn = get_db()
            db = conn.cursor()
            user = "DELETE FROM t_user where id=0"
            db.execute(user)
            notice = "DELETE from t_notice where id in (1,2,3)"
            db.execute(notice)
            conn.commit()
            conn.close()
        except Exception as e:
            print(e)
    request.addfinalizer(fin)
