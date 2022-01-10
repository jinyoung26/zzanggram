from flask import Flask, render_template, jsonify, request, url_for, redirect
from pymongo import MongoClient
import jwt
import datetime
import hashlib

app = Flask(__name__)

client = MongoClient('mongodb+srv://zzanggram1:1234@cluster0.llu3g.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

SECRET_KEY = 'YOUNG'

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

@app.route('/login', methods=['POST'])
def login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    print(id_receive, pw_receive)

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.member.find_one({'id': id_receive, 'pw': pw_hash})

    print(result)


    if result is not None:
        payload = {
            'id' : id_receive,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=3)
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
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    repw_receive = request.form['repw_give']
    nick_receive = request.form['nick_give']
    name_receive = request.form['name_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    repw_hash = hashlib.sha256(repw_receive.encode('utf-8')).hexdigest()

    doc = {
        'id': id_receive,
        'pw': pw_hash,
        'repw' : repw_hash,
        'nick': nick_receive,
        'name': name_receive
    }

    db.member.insert_one(doc)
    return jsonify({'result': 'success'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)