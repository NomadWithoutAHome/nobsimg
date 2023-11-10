from io import BytesIO

from fastapi import FastAPI, UploadFile, File, HTTPException
from deta import Deta
import shutil
import os

from starlette.responses import HTMLResponse
from fastapi.responses import StreamingResponse

app = FastAPI()

# Initialize Deta
deta = Deta('b0cCEPwBs3YG_s8VNWEAdjAo93RMYsgidhwUgKxt86NZo')  # replace 'project_key' with your actual project key
drive = deta.Drive('images')  # 'images' is the name of your drive

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    # Check if the uploaded file is an image
    image_formats = ["jpg", "jpeg", "png", "gif", "bmp"]
    if file.filename.split(".")[-1] not in image_formats:
        raise HTTPException(status_code=400, detail="Unsupported file format.")

    # Upload file to Deta Space
    drive.put(file.filename, file.file)

    # Return the URL of the uploaded file
    url = f"https://img.nobss.online/files/{file.filename}"
    return {"filename": file.filename, "url": url}

@app.get("/")
async def root():
    files = drive.list()['names']
    print(files)
    html = "<h2>Files in Deta Drive:</h2>"
    for file in files:
        html += f"<p>{file}</p>"
    return HTMLResponse(content=html)

@app.get("/files/{name}")
async def get_file(name: str):
    try:
        data = drive.get(name)
        data_bytes = BytesIO(data.read())
        return StreamingResponse(data_bytes, media_type="image/png")
    except Exception as e:
        return {"error": "Error retrieving file"}

# @app.get("/files/download/{name}")
# def download_img(name: str):
#     res = drive.get(name)
#     return Response(res.iter_chunks(1024),
#                     content_type="image/png")