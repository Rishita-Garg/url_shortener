from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import models, database
import random, string

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/shorten")
def shorten_url(request: Request, original_url: str = Form(...)):
    db = database.SessionLocal()
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    url = models.URL(original_url=original_url, short_code=code)
    db.add(url)
    db.commit()
    db.refresh(url)
    return templates.TemplateResponse("index.html", {"request": request, "shortened": f"http://localhost:8000/{code}"})

@app.get("/{short_code}")
def redirect(short_code: str):
    db = database.SessionLocal()
    url = db.query(models.URL).filter(models.URL.short_code == short_code).first()
    if url:
        return RedirectResponse(url.original_url)
    return {"error": "URL not found"}
