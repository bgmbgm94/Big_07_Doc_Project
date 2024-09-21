from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
import requests
import os


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (특정 도메인만 허용하려면 ["http://example.com"] 형식으로 변경)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)
# Middleware to disable caching for all responses
@app.middleware("http")
async def no_cache_middleware(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# 절대 경로 설정
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))

# Static files
app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "static")), name="static")

# Templates
templates = Jinja2Templates(directory=os.path.join(frontend_dir, "templates"))

# HTML 파일 제공
@app.get("/", response_class=FileResponse)
async def get_root():
    return os.path.join(frontend_dir, "templates/index.html")

@app.get("/template")
async def get_template(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(frontend_dir, "static/favicon.ico"))

@app.post("/ask")
async def proxy_ask(request: Request):
    payload = await request.json()
    response = requests.post(f"http://10.0.136.43:1234/ask",json=payload)
    return response.json()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    