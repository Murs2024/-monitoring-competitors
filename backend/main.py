"""
Главный модуль FastAPI. Мониторинг конкурентов — MVP ассистент.
"""
import base64
import sys
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response

from backend.config import settings
from backend.models.schemas import (
    TextAnalysisRequest,
    TextAnalysisResponse,
    ImageAnalysisResponse,
    ParseDemoRequest,
    ParseDemoResponse,
    ParsedContent,
    HistoryResponse,
)
from backend.services.openai_service import openai_service
from backend.services.parser_service import parser_service
from backend.services.history_service import history_service

# Путь к frontend: при запуске из exe — из упакованной папки _MEIPASS
if getattr(sys, "frozen", False) and getattr(sys, "_MEIPASS", None):
    FRONTEND_DIR = Path(sys._MEIPASS) / "frontend"
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    FRONTEND_DIR = (PROJECT_ROOT / "frontend").resolve()

app = FastAPI(
    title="Мониторинг конкурентов",
    description="MVP ассистент для анализа конкурентов (текст и изображения)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Главная страница — фронтенд."""
    index = FRONTEND_DIR / "index.html"
    if not index.exists():
        return {"message": "Frontend not found. Add frontend/index.html."}
    return FileResponse(index)


@app.get("/favicon.ico")
async def favicon():
    """Фавикон — флаг РФ (SVG)."""
    path = FRONTEND_DIR / "favicon.svg"
    if path.exists():
        return FileResponse(path, media_type="image/svg+xml")
    return Response(status_code=204)

@app.post("/analyze_text", response_model=TextAnalysisResponse)
def analyze_text(request: TextAnalysisRequest):
    """Анализ текста конкурента."""
    try:
        analysis = openai_service.analyze_text(request.text)
        history_service.add_entry(
            request_type="text",
            request_summary=request.text[:100] + "..." if len(request.text) > 100 else request.text,
            response_summary=analysis.summary,
            details={"analysis": analysis.model_dump()},
        )
        return TextAnalysisResponse(success=True, analysis=analysis)
    except Exception as e:
        return TextAnalysisResponse(success=False, error=str(e))


@app.post("/analyze_image", response_model=ImageAnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """Анализ изображения конкурента."""
    allowed = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый тип файла. Разрешены: {', '.join(allowed)}",
        )
    try:
        content = await file.read()
        image_base64 = base64.b64encode(content).decode("utf-8")
        analysis = openai_service.analyze_image(
            image_base64=image_base64,
            mime_type=file.content_type or "image/jpeg",
        )
        history_service.add_entry(
            request_type="image",
            request_summary=f"Изображение: {file.filename}",
            response_summary=(analysis.description or "Анализ изображения")[:200],
            details={"analysis": analysis.model_dump()},
        )
        return ImageAnalysisResponse(success=True, analysis=analysis)
    except Exception as e:
        return ImageAnalysisResponse(success=False, error=str(e))


@app.post("/parse_demo", response_model=ParseDemoResponse)
async def parse_demo(request: ParseDemoRequest):
    """Парсинг и анализ сайта конкурента (демо)."""
    try:
        title, h1, first_paragraph, error = await parser_service.parse_url(request.url)
        if error:
            return ParseDemoResponse(success=False, error=error)
        analysis = openai_service.analyze_parsed_content(
            title=title, h1=h1, paragraph=first_paragraph
        )
        parsed_content = ParsedContent(
            url=request.url,
            title=title,
            h1=h1,
            first_paragraph=first_paragraph,
            analysis=analysis,
        )
        history_service.add_entry(
            request_type="parse",
            request_summary=f"URL: {request.url}",
            response_summary=title or "N/A",
            details=parsed_content.model_dump(),
        )
        return ParseDemoResponse(success=True, data=parsed_content)
    except Exception as e:
        return ParseDemoResponse(success=False, error=str(e))


@app.get("/history", response_model=HistoryResponse)
async def get_history():
    """Получить историю последних запросов."""
    items = history_service.get_history()
    return HistoryResponse(items=items, total=len(items))


@app.delete("/history")
async def clear_history():
    """Очистить историю."""
    history_service.clear_history()
    return {"success": True, "message": "История очищена"}


@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса."""
    return {
        "status": "healthy",
        "service": "Competitor Monitor",
        "version": "1.0.0",
    }


if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
