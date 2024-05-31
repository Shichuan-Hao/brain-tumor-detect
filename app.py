#!/usr/bin/python
# coding=utf-8
import cv2
import sqlite3
import hashlib
import tensorflow as tf
import numpy as np

from PIL import Image
from flask import Flask, render_template, jsonify, request, session
from tensorflow.keras.models import load_model, Model
from datetime import datetime

from module.snowflake import Snowflake

gpus = tf.config.list_physical_devices("GPU")

if gpus:
    gpu0 = gpus[0]  # 如果有多个GPU，仅使用第0个GPU
    tf.config.experimental.set_memory_growth(gpu0, True)  # 设置GPU显存用量按需使用
    tf.config.set_visible_devices([gpu0], "GPU")

print('gpus:', gpus)

height, width = 224, 224
# 标签类比
class_name_dict = {0: '无肿瘤', 1: '胶质瘤', 2: '垂体瘤', 3: '脑膜瘤'}


app = Flask(__name__)
app.secret_key = 'this_is_a_secret_key' # 设置一个用于会话加密的密钥


# login_name = None
login_user_id = None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test_predict')
def test_predict():
    return render_template('test_predict.html')

@app.route('/login')
def route_login():
    return render_template('login.html')

@app.route('/register')
def route_register():
    return render_template('register.html')

@app.route('/mine')
def mine():
    return render_template('mine.html')


# ------------ API 接口 -------------
## name, idNo, email, age, sex, password
@app.route('/register', methods=['POST'])
def register():
    conn = sqlite3.connect('user_info.db')
    cursor = conn.cursor()

    check_sql = "SELECT * FROM sqlite_master where type='table' and name='user'"
    cursor.execute(check_sql)
    results = cursor.fetchall()
    
    # 数据库表不存在
    if len(results) == 0:
        # 创建数据库表
        sql = """
                CREATE TABLE user(
                    id CHAR(256) NOT NULL,
                    name CHAR(256),
                    idNo CHAR(256),
                    email CHAR(256),
                    age CHAR(256),
                    sex CHAR(256),
                    password CHAR(256),
                    create_time CHAR(256),
                    update_time CHAR(256),
                    PRIMARY KEY ("id")
                );
                """
        cursor.execute(sql)
        conn.commit()
        print('创建数据库表成功！')

    sql = "INSERT INTO user (id, name, idNo, email, age, sex, password, create_time, update_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"

    id = Snowflake(0,0).next_id()
    name = request.form.get('name')
    idNo = request.form.get('idNo')
    email = request.form.get('email')
    age = request.form.get('age')
    sex = request.form.get('sex')
    # 密码
    password = request.form.get('password')
    passwordMd5 = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()
    create_time = datetime.now().timestamp()
    update_time = datetime.now().timestamp()

    cursor.executemany(sql, [(id, name, idNo, email, age, sex, passwordMd5, create_time, update_time)])
    conn.commit()
    return jsonify({'info': '用户注册成功！', 'status': 'ok'})


@app.route('/login', methods=['POST'])
def login():
    # global login_user_id
    conn = sqlite3.connect('user_info.db')
    cursor = conn.cursor()

    name = request.form.get('name')
    password = request.form.get('password')
    passwordMd5 = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()

    sql = "select id,name from user where name=? and password=?"
    cursor.execute(sql, (name, passwordMd5))
    results = cursor.fetchall()

    # 打印输出 results 的内容
    print("Results:", results)

    if len(results) > 0:
        # 打印输出内容
        for row in results:
            print(f"User ID: {row[0]}")
            print(f"User Name: {row[1]}", )
        # 放入 flask seesion
        session['user_id'] = results[0][0]
        session['user_name'] = results[0][1]
        # return jsonify({'info': '登录成功！', 'status': 'ok'})
        return jsonify({'info': name + '用户登录成功！', 'status': 'ok'})
    else:
        return jsonify({'info': '当前用户不存在！', 'status': 'error'})


# @app.route('/check_login')
# def check_login():
#     """判断用户是否登录"""

#     return jsonify({'username': login_name, 'login': login_name is not None})
    
@app.route('/check_login')
def check_login():
    """判断用户是否登录"""
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    if user_id:
        return jsonify({'username': user_name, 'login': True})
    else:
        return jsonify({'login': False})

@app.route('/logout', methods=['GET'])
def logout():
    """用户退出"""
    session.pop('user_id', None)
    session.pop('user_name', None)
    return jsonify({'message': 'Logout successful'})

# 加载训练好的模型权重
print("load VGG16 weights...")
model_vgg16 = load_model('./save_models/vgg16_best.h5')

print("load Inception-V3 weights...")
model_inceptionv3 = load_model('./save_models/inceptionv3_best.h5')


@app.route('/submit_and_predict', methods=['POST'])
def submit_and_predict():
    """
    脑部肿瘤图像识别
    """
    model_type = request.form['model_type']
    test_file = request.files['file']
    filename = test_file.filename

    # 保存上传的文件
    test_file_path = './static/img/predict_test/{}'.format(filename)
    test_file.save(test_file_path)

    image = cv2.imread(test_file_path)
    image_fromarray = Image.fromarray(image, 'RGB')
    resize_image = image_fromarray.resize((height, width))
    resize_image = np.array(resize_image) / 255
    test_X = np.array([resize_image])

    if model_type == "VGG16":
        predictions = model_vgg16.predict(test_X)
    else:
        predictions = model_inceptionv3.predict(test_X)

    pred_labels = np.argmax(predictions, 1)[0]
    print(pred_labels)
    predict_class = class_name_dict[pred_labels]
    print("预测结果为：", predict_class)
    print(test_file_path)
    save_predict(test_file_path, predict_class)
    result = {
        "upload_image": test_file_path,
        "predict": predict_class
    }
    print(result)
    return jsonify(result)

def save_predict(test_file_path, predict_result):
    user_id = session['user_id']
    user_name = session['user_name']

    conn = sqlite3.connect('user_info.db')
    cursor = conn.cursor()

    check_sql = "SELECT * FROM sqlite_master where type='table' and name='predict_result'"
    cursor.execute(check_sql)
    results = cursor.fetchall()

    cursor.execute(check_sql)
    results = cursor.fetchall()
    
    # 数据库表不存在
    if len(results) == 0:
        # 创建数据库表
        sql = """
                CREATE TABLE predict_result(
                    id CHAR(256) NOT NULL,
                    user_id CHAR(256),
                    user_name CHAR(256),
                    file_address CHAR(256),
                    result CHAR(256),
                    create_time CHAR(256),
                    update_time CHAR(256),
                    PRIMARY KEY ("id")
                );
                """
        cursor.execute(sql)
        conn.commit()
        print('创建数据库表成功！')

    sql = "INSERT INTO predict_result (id, user_id, user_name, file_address, result, create_time, update_time) VALUES (?, ?, ?, ?, ?, ?, ?);"
    id = Snowflake(0,0).next_id()
    create_time = datetime.now().timestamp()
    update_time = datetime.now().timestamp()
    cursor.executemany(sql, [(id, user_id, user_name, test_file_path, predict_result, create_time, update_time)])
    conn.commit()
    
@app.route('/user_info', methods=['GET'])
def user_info():
    user_id = session['user_id']
    user_name = session['user_name']
    print(f"用户标识：{user_id}")

    # global login_user_id
    conn = sqlite3.connect('user_info.db')
    cursor = conn.cursor()

    sql = "select idNo,email,age,sex from user where id=?"
    cursor.execute(sql, (user_id,))
    results = cursor.fetchall()

    # 打印输出 results 的内容
    print("Results:", results)

    if len(results) > 0:
        # 打印输出内容
        for row in results:
            id_no = row[0]
            email = row[1]
            age = row[2]
            sex = row[3]
            print(f"User ID: {id_no}")
            print(f"User Email: {email}")
            print(f"User Age: {age}")
            print(f"User Sex: {sex}")
        result = {
            "name": user_name,
            "id_no": id_no,
            "email": email,
            "age": age,
            "sex": sex
        }
        print(result)
        return jsonify(result)
    else:
        return jsonify({'message': '获取获取到用户信息'})
    
@app.route('/predict_result_paged', methods=['POST'])
def predict_result_paged():
    user_id = session['user_id']
    user_name = session['user_name']

    # 获取请求参数中的页码和每页条数，默认为第一页和每页3条
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 3))

    # 计算 LIMIT 和 OFFSET
    limit = page_size
    offset = (page - 1) * page_size

    conn = sqlite3.connect('user_info.db')
    cursor = conn.cursor()

    sql = "SELECT file_address, result, create_time FROM predict_result LIMIT ? OFFSET ?"
    cursor.execute(sql, (limit, offset))
    items = cursor.fetchall()

    # 打印输出 results 的内容
    print("Results:", items)

    result = {
        "page": page,
        "page_size": page_size,
        "total_pages": 0,
        "items": []
    }

    if len(items) > 0:
        # 获取总记录数来计算总页数
        cursor.execute("SELECT COUNT(*) FROM predict_result")
        total_items = cursor.fetchone()[0]
        total_pages = (total_items + page_size - 1) // page_size  # 向上取整
        result["total_pages"] = total_pages

        for item in items:
            result["items"].append({
                "file_address": item[0],
                "predict_result": item[1],
                "create_time": item[2]
            })

    return jsonify({'result': result, 'status': 'ok'})
        

if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=False)
