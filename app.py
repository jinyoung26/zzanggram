from flask import Flask, render_template, jsonify, request, url_for, redirect
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from uuid import uuid4

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./static/upload_img/"

client = MongoClient('mongodb+srv://zzanggram1:1234@cluster0.llu3g.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

SECRET_KEY = 'YOUNG'

def email_check(email_receive):
    return bool(db.users.find_one({'email': email_receive}))

def token_valid():
    token_receive = request.cookies.get('token')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return jsonify ({'result': 'fail', 'msg': "로그인 시간이 만료되었습니다."})
    except jwt.exceptions.DecodeError:
        return jsonify ({'result': 'fail', 'msg': "로그인 정보가 없습니다."})

@app.route('/')
def home():
    token = token_valid()
    print(type(token))

    if type(token) == dict:
        return render_template("main_page.html")
    else:
        return redirect(url_for("login"))


@app.route('/login')
def loginpage():
   return render_template('login.html')

@app.route('/main_page')
def mainpage():
   return render_template('main_page.html')

@app.route('/upload')
def uploadpage():
   return render_template('upload.html')

@app.route('/login', methods=['POST'])
def login():
    email_receive = request.form['email_give']
    pw_receive = request.form['pw_give']

    print(email_receive, pw_receive)

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.users.find_one({'email': email_receive, 'pw': pw_hash})

    print(result)


    if result is not None:
        payload = {
            'email' : email_receive,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})

    else:
        return jsonify({'result': 'fail'})

@app.route('/sign_up')
def sign_up():
   return render_template('/sign_up.html')

@app.route("/sign_up", methods=["POST"])
def sign():
    email_receive = request.form['email_give']
    pw_receive = request.form['pw_give']
    repw_receive = request.form['repw_give']
    nick_receive = request.form['nick_give']
    name_receive = request.form['name_give']

    if pw_receive != repw_receive:
        return jsonify({'result': 'error', 'msg': '비밀번호가 일치하지 않습니다.'})

    elif not (email_receive and pw_receive and repw_receive and name_receive and nick_receive):
        return jsonify({'result': 'error', 'msg': '빈 칸을 입력해주세요.'})

    elif email_check(email_receive):
        return jsonify({'result': 'error', 'msg': '중복된 이메일입니다.'})

    elif "@" and "." not in email_receive:
        return jsonify({'result': 'error', 'msg': '이메일 형식이 아닙니다.'})

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    doc = {
        'email': email_receive,
        'pw': pw_hash,
        'nick': nick_receive,
        'name': name_receive
    }

    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/upload', methods=['POST'])
def file_upload():
    token = token_valid()
    title_receive = request.form['title_give']
    # print(title_receive)
    file = request.files['file_give']
    extension = file.filename.split('.')[-1]
    # print(file)
    # print(extension)
    img_name = uuid4().hex
    filename = f'{title_receive}-{img_name}'

    save_to = f'static/upload_img/{filename}.{extension}'
    file.save(save_to)

    doc = {'title': title_receive,
            'img':f'{filename}.{extension}'
           }

    db.upload.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/imgshow/<title>')
def img_show(title):
    img_info = db.upload.find_one({'title': title})
    # print(img_info)
    return render_template('showimg.html', img_info=img_info)

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)