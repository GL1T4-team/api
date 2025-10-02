from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["https://gl1t4-team-client-51eb.twc1.net"],
    allow_methods = ["*"],
    allow_headers = ["*"]
)

@app.get("/")
async def root():
    return "ok"

@app.get("/upload_file")
async def upload_file(file: UploadFile):
    from parser import parse_csv

    if file.content_type == 'text/csv':
        data, skipped_rows = parse_csv(file.file)
        return JSONResponse({'skipped_rows':skipped_rows})