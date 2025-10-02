from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import json

def format_data(data):
    res = []
    for row in data:
        res.append((row['flight_id'],row['uav_type'],row['flight_region'],json.dumps(row['departure_coords']),json.dumps(row['arrival_coords']),row['flight_date'],row['start_time'],row['end_time']))

    return res

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["https://gl1t4-team-client-51eb.twc1.net","http://gl1t4-team-client-51eb.twc1.net","http://127.0.0.1:8000","https://glitch-team.ru","http://glitch-team.ru"],
    allow_methods = ["*"],
    allow_headers = ["*"],
    allow_credentials = True
)

@app.get("/")
async def root():
    return "ok"

@app.post("/upload_file")
async def upload_file(file: UploadFile):
    from parser import parse_csv
    from database import DB

    if file.content_type == 'text/csv':
        data, skipped_rows = parse_csv(file.file)
        DB().upload_data(format_data(data))
        return JSONResponse({'skipped_rows':skipped_rows})