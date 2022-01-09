from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
app = Flask(__name__)

client = MongoClient('mongodb+srv://zzanggram1:1234@cluster0.llu3g.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/')
def loginpage():
   return render_template('/login.html')

@app.route('/mainpage')
def mainpage():
   return render_template('/main_page.html')

@app.route('/', methods=['POST'])
def login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    result = db.member.find_one({'id':id_receive, 'pw':pw_receive})
    if result is not None:
        return jsonify({'result': 'success'})
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

    doc = {
        'id': id_receive,
        'pw': pw_receive,
        'repw' : repw_receive,
        'nick': nick_receive,
        'name': name_receive
    }

    db.member.insert_one(doc)
    return jsonify({'result': 'success'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)