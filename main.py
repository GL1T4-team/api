from fastapi import FastAPI, UploadFile
from starlette.applications import Starlette

app = FastAPI()

@app.post("/upload_file")
async def upload_file(file: UploadFile):
    from parser import parse_csv

    if file.content_type == 'text/csv':
        data, skipped_rows = parse_csv(file.file)
        return {'data':data, 'skipped_rows':skipped_rows}
