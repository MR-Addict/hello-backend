import os
import shutil
import uvicorn
from tinydb import TinyDB, Query
from tinydb.operations import increment
from typing import Union
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.staticfiles import StaticFiles

db_folder = 'db/'
endpoint = '/uploads/'
upload_folder = 'public/uploads/'

query = Query()
app = FastAPI(
    title="Hello API",
    version="1.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)


def storeFiles(path, preview, sources):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, preview.filename), "wb") as buffer:
        shutil.copyfileobj(preview.file, buffer)
    for file in sources:
        with open(os.path.join(path, file.filename), "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)


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


@app.get('/api/v1/click/{id}')
async def handle_click_upload(id):
    db = TinyDB(db_folder+'db.json')
    get_record = db.get(query.id == id)
    if get_record:
        db.update(increment('views'), query.id == id)
        get_record = db.get(query.id == id)
        return {"status": True, "msg": get_record}
    return {"status": False, "msg": 'Failed'}


@app.get('/api/v1/uploads')
async def get_all_uploads():
    db = TinyDB(db_folder+'db.json')
    get_records = db.all()
    return {"status": True, "msg": get_records[::-1]}


@app.delete('/api/v1/delete/{id}')
async def handle_delete_upload(id):
    db = TinyDB(db_folder+'db.json')
    get_record = db.get(query.id == id)
    if get_record and os.path.exists(upload_folder+id):
        db.remove(query.id == id)
        shutil.rmtree(upload_folder+id)
        return {"status": True, "msg": get_record}
    return {"status": False, "msg": 'Failed'}


@app.post('/api/v1/upload')
async def handle_submit_upload(
    id: str = Form(), info: str = Form(),
    preview: UploadFile = File(), sources: list[UploadFile] = File()
):
    try:
        link = endpoint+id+'/'
        img = endpoint+id+'/'+preview.filename
        storeDB(id, info, link, img)
        storeFiles(upload_folder + id, preview, sources)
        return {"status": True, "msg": {"link": link}}
    except:
        return {"status": False, "msg": "Failed"}


app.mount("/", StaticFiles(directory="public", html=True), name="public")
if __name__ == "__main__":
    os.makedirs(db_folder, exist_ok=True)
    uvicorn.run("index:app", host="0.0.0.0", port=8090, log_level="info")
