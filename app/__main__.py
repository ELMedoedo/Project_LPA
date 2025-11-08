from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.weather import get_weather_data

app = FastAPI(title="Weather API", description="Получение текущей температуры в городе")


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/weather/")
def get_weather(city: str, request: Request):
    """
    Получить текущую температуру в городе
    
    - city- Название города 
    """
    try:
        weather_data = get_weather_data(city)
        if "text/html" in request.headers.get("accept", ""):   #если запрос приходит из браузера
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "weather": weather_data,
                    "city": city
                }
            )

    except Exception as e:
        error_message = f"Ошибка получения данных: {str(e)}"
        if "text/html" in request.headers.get("accept", ""):
            return templates.TemplateResponse(
                "index.html", 
                {
                    "request": request, 
                    "error": error_message,
                    "city": city
                }
            )
        
        raise HTTPException(status_code=400, detail=error_message)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """Главная страница с формой"""
    return templates.TemplateResponse("index.html", {"request": request})

