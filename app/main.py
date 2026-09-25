from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.api_routes import router as api_router
from app.auth import authenticate_user
from app.config import (
    get_app_host,
    get_app_port,
    get_cors_origins,
    get_session_secret,
    normalize_email,
    password_meets_policy,
)
from app.db import Base, engine, get_db
from app.models import User

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="GymVe", docs_url=None, redoc_url=None, lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=get_session_secret(), https_only=False)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def _session_user(request: Request, db: Session) -> dict | None:
    email = request.session.get("email")
    if not email:
        return None
    user = db.query(User).filter(User.email == normalize_email(email)).one_or_none()
    if not user:
        request.session.clear()
        return None
    return {"email": user.email, "display_name": user.display_name}


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    if _session_user(request, db):
        return RedirectResponse(url="/inicio", status_code=303)
    return RedirectResponse(url="/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    if _session_user(request, db):
        return RedirectResponse(url="/inicio", status_code=303)
    return templates.TemplateResponse(
        request,
        "login.html",
        {"error": None, "user": None},
    )


@app.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    ok, policy_msg = password_meets_policy(password)
    if not ok:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": policy_msg, "user": None, "email": email},
            status_code=400,
        )
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            request,
            "login.html",
            {
                "error": "Correo o contraseña incorrectos.",
                "user": None,
                "email": email,
            },
            status_code=401,
        )
    request.session["email"] = user.email
    return RedirectResponse(url="/inicio", status_code=303)


@app.get("/inicio", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user = _session_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "home.html", {"user": user})


@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@app.get("/manifest.webmanifest")
async def manifest():
    return RedirectResponse(url="/static/manifest.webmanifest", status_code=307)


@app.get("/health")
async def health():
    return {"status": "ok"}


def run():
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=get_app_host(),
        port=get_app_port(),
        reload=False,
    )


if __name__ == "__main__":
    run()
