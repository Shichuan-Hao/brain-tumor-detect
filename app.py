#!/usr/bin/python
# coding=utf-8
import cv2
import sqlite3
import hashlib
from flask import Flask, render_template, jsonify, request
from tensorflow.keras.models import load_model, Model
import tensorflow as tf
from PIL import Image
import numpy as np
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
login_name = None


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


# ------------ API 接口 -------------
@app.route('/check_login')
def check_login():
    """判断用户是否登录"""
    return jsonify({'username': login_name, 'login': login_name is not None})


## name, idNo, email, age, sex, password
@app.route('/register')
def register(name, password):
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
                    image CHAR(256),
                    result CHAR(256),
                    PRIMARY KEY ("id")
                );
                """
        cursor.execute(sql)
        conn.commit()
        print('创建数据库表成功！')

    sql = "INSERT INTO user (id, name, idNo, email, age, sex, password) VALUES (?,?,?,?,?,?,?);"

    id = Snowflake(1,1).next_id()
    name = request.form.get('name')
    idNo = request.form.get('idNo')
    email = request.form.get('email')
    age = request.form.get('age')
    sex = request.form.get('sex')
    password = request.form.get('password')
    passwordMd5 = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()

    cursor.executemany(sql, [(id, name, idNo, email, age, sex, passwordMd5)])
    conn.commit()
    return jsonify({'info': '用户注册成功！', 'status': 'ok'})


@app.route('/login', methods=['POST'])
def login():
    global login_name
    conn = sqlite3.connect('user_info.db')
    cursor = conn.cursor()

    # check_sql = "SELECT * FROM sqlite_master where type='table' and name='user'"
    # cursor.execute(check_sql)
    # results = cursor.fetchall()
    # 数据库表不存在
    # if len(results) == 0:
        # # 创建数据库表
        # sql = """
        #         CREATE TABLE user(
        #             name CHAR(256),
        #             idNo CHAR(256),
        #             email CHAR(256),
        #             age CHAR(256),
        #             sex CHAR(256),
        #             password CHAR(256)
        #         );
        #         """
        # cursor.execute(sql)
        # conn.commit()
        # print('创建数据库表成功！')
    name = request.form.get('name')
    password = request.form.get('password')

    passwordMd5 = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()

    sql = "select * from user where name='{}' and password='{}'".format(name, passwordMd5)
    cursor.execute(sql)
    results = cursor.fetchall()

    login_name = name
    if len(results) > 0:
        # return jsonify({'info': '登录成功！', 'status': 'ok'})
        return jsonify({'info': name + '用户登录成功！', 'status': 'ok'})
    else:
        return jsonify({'info': '当前用户不存在！', 'status': 'error'})


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
    result = {
        "upload_image": test_file_path,
        "predict": predict_class
    }
    print(result)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=False)
