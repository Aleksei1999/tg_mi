
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader
import os, uuid, shutil, zipfile
from telegram_bot_auto import set_bot_menu_button, generate_miniapp_link

app = FastAPI()

env = Environment(loader=FileSystemLoader("templates"))

class AppDescription(BaseModel):
    description: str

def parse_description(text):
    return {
        "title": "Форма записи",
        "header": "Запишитесь на курс",
        "fields": [
            {"label": "Имя", "name": "name", "type": "text"},
            {"label": "Email", "name": "email", "type": "email"},
            {"label": "Телефон", "name": "phone", "type": "tel"},
        ],
        "button_text": "Записаться на курс",
        "success_message": "Спасибо! Вы записались!"
    }

@app.post("/generate")
async def generate_miniapp(data: AppDescription):
    parsed = parse_description(data.description)
    app_id = str(uuid.uuid4())
    out_dir = f"generated/{app_id}"
    os.makedirs(out_dir, exist_ok=True)

    html_tpl = env.get_template("index.html.jinja")
    with open(f"{out_dir}/index.html", "w", encoding="utf-8") as f:
        f.write(html_tpl.render(**parsed))

    js_tpl = env.get_template("script.js.jinja")
    with open(f"{out_dir}/script.js", "w", encoding="utf-8") as f:
        f.write(js_tpl.render(**parsed))

    with open(f"{out_dir}/style.css", "w") as f:
        f.write("body { font-family: sans-serif; padding: 20px; }")

    zip_path = f"generated/{app_id}.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in os.listdir(out_dir):
            zipf.write(os.path.join(out_dir, filename), arcname=filename)

    webapp_url = f"https://yourdomain.com/generated/{app_id}/index.html"
    telegram_link = generate_miniapp_link(app_id)
    set_bot_menu_button(webapp_url)

    return JSONResponse({
        "preview_url": webapp_url,
        "zip_url": f"/generated/{app_id}.zip",
        "telegram_link": telegram_link
    })

@app.get("/generated/{file_path:path}")
async def serve_file(file_path: str):
    return FileResponse(path=f"generated/{file_path}")
