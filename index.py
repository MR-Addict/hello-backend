import os
import shutil
from tinydb import TinyDB, Query
from tinydb.operations import increment
from flask import Flask, request, send_from_directory
from flask_cors import CORS

port = 8090
db_folder = 'db/'
endpoint = '/uploads/'
upload_folder = 'public/uploads/'

app = Flask(__name__, static_folder='public')
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resources={r"*": {"origins": "*"}})
query = Query()

    
def storeFiles(path, files):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
    for file in files.getlist('preview'):
        file.save(os.path.join(path, file.filename))
    for file in files.getlist('sources'):
        file.save(os.path.join(path, file.filename))


def storeDB(id, info, link, img):
    db = TinyDB(db_folder+'db.json')
    get_record = db.get(query.id == id)
    ins_record = {'id': id, 'info': info, "link": link, 'img': img}
    if get_record:
        get_record.update(ins_record)
        db.update(get_record, query.id == id)
    else:
        ins_record.update({'views': 0})
        db.insert(ins_record)


@app.route('/<path:filename>', methods=["GET"])
def route_static_files(filename):
    return send_from_directory(app.static_folder, filename)


@app.route('/', methods=["GET"])
def route_home_get():
    return send_from_directory(app.static_folder, "index.html")


@ app.route('/api/v1/click/<path:id>', methods=['GET'])
def route_click(id):
    db = TinyDB(db_folder+'db.json')
    get_record = db.get(query.id == id)
    if get_record:
        db.update(increment('views'), query.id == id)
        get_record = db.get(query.id == id)
        return {"status": True, "msg": get_record}
    return {"status": False, "msg": 'Failed'}


@ app.route('/api/v1/delete/<path:id>', methods=['DELETE'])
def route_delete(id):
    db = TinyDB(db_folder+'db.json')
    get_record = db.get(query.id == id)
    if get_record and os.path.exists(upload_folder+id):
        db.remove(query.id == id)
        shutil.rmtree(upload_folder+id)
        return {"status": True, "msg": get_record}
    return {"status": False, "msg": 'Failed'}


@ app.route('/api/v1/all', methods=['GET'])
def route_all():
    db = TinyDB(db_folder+'db.json')
    get_records = db.all()
    return {"status": True, "msg": get_records[::-1]}


@ app.route('/api/v1/submit', methods=["POST"])
def route_submit():
    if request.files and request.form and 'preview' in request.files and 'sources' in request.files and 'id' in request.form and 'info' in request.form:
        id = request.form['id']
        info = request.form['info']
        try:
            link = endpoint+id+'/index.html'
            img = endpoint+id+'/'+request.files.getlist('preview')[0].filename
            storeDB(id, info, link, img)
            storeFiles(upload_folder + id, request.files)
            return {"status": True, "msg": {"link": link}}
        except:
            return {"status": False, "msg": "Failed"}
    else:
        return {"status": False, "msg": "Failed"}


if __name__ == '__main__':
    os.makedirs(db_folder, exist_ok=True)
    app.run(host="0.0.0.0", port=port, debug=True)
