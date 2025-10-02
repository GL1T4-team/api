from fastapi import FastAPI, UploadFile
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse

from content_size_limit_asgi import ContentSizeLimitMiddleware

app = FastAPI()
app.add_middleware(ContentSizeLimitMiddleware, max_content_size=20_000_000)

@app.post("/upload_file")
async def upload_file(file: UploadFile):
    from parser import parse_csv

    if file.content_type == 'text/csv':
        data, skipped_rows = parse_csv(file.file)
        return {'data':data, 'skipped_rows':skipped_rows}
