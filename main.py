from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://127.0.0.1:8000"],
    allow_methods = ["*"],
    allow_headers = ["*"]
)

@app.post("/upload_file")
async def upload_file(file: UploadFile):
    from parser import parse_csv

    if file.content_type == 'text/csv':
        data, skipped_rows = parse_csv(file.file)
        return {'data':data, 'skipped_rows':skipped_rows}
