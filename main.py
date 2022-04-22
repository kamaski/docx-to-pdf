from pathlib import Path
from typing import Any, Dict

import aiofiles
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Json

import config
from convert import Convert
from render import Render
from schemas import Client, get_translit_client, get_list_data_sanction, compare_and_answer


app = FastAPI()


class Data(BaseModel):
    file_path: str
    content: Json


@app.post("/upload-template")
async def upload_template(file: UploadFile = File(...)):
    file_path = Path(config.TEMPLATES_DIR / file.filename)
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    return {"filename": file_path}


@app.post("/download-converted", response_class=FileResponse)
def download_converted(data: Data):
    rendered_file: Path = Render.render_file(data.file_path, data.content)
    converted_file: Path = Convert.convert_file(rendered_file)
    if not converted_file.exists():
        raise HTTPException(status_code=500, detail="Failed to convert file.")
    return converted_file


@app.post("/convert", response_class=FileResponse)
async def convert(file: UploadFile = File(...)):
    file_path = Path(config.RENDERED_DIR / file.filename)
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    converted_file: Path = Convert.convert_file(file_path)
    if not converted_file.exists():
        raise HTTPException(status_code=500, detail="Failed to convert file.")
    return converted_file


@app.post('/check_blacklist')
def check_blacklist(client: Client):
    # чистые полученные даннные
    not_translit_client = f"{client.name} {client.surname} {client.pater_name} {client.date_of_birth.strftime('%Y-%m-%d')} {client.place_of_birth} {client.nationality}"
    fio_client = f"{client.name} {client.surname} {client.pater_name}"
    # переведенные полученные данные
    translit_client, fio_translit_client = get_translit_client(client)
    sanction_list, fio_client_list, id = get_list_data_sanction()
    # сравнивание по чистым данным
    not_tran_data = compare_and_answer(sanction_list, not_translit_client, id)
    not_tran_fio = compare_and_answer(fio_client_list, fio_client, id)
    if not_tran_data:
        return {"sanction": 1, "id": not_tran_data}
    if not_tran_fio:
        return {"sanction": 1, "id": not_tran_fio}

    # сравнивание по переведенным данным
    tran_data = compare_and_answer(sanction_list, translit_client, id)
    fio_tran_data = compare_and_answer(fio_client_list, fio_translit_client, id)
    if tran_data:
        return {"sanction": 1, "id": not_tran_data}
    if fio_tran_data:
        return {"sanction": 1, "id": fio_tran_data}

    return {"sanction": 0}
