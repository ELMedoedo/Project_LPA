from fastapi import FastAPI, HTTPException, Request, Path, Query
from fastapi.responses import HTMLResponse
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from typing import List
from app.weather import get_weather_data

app = FastAPI(title="Weather API", description="Получение текущей температуры в городе")


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Pydantic модели для API
class WeatherResponse(BaseModel):
    city: str
    country: str
    temperature: float
    feels_like: float
    description: str
    humidity: int
    pressure: int
    wind_speed: float
    visibility: str

class ErrorResponse(BaseModel):
    detail: str

# Web Interface

@app.get("/weather/", include_in_schema=False)
def get_weather_web(city: str = Query(..., description="Название города"), request: Request = None):
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

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def read_root(request: Request):
    """Главная страница с формой"""
    return templates.TemplateResponse("index.html", {"request": request})

# REST API Endpoints
@app.get(
    "/api/v1/weather/{city}",
    response_model=WeatherResponse,
    responses={
        200: {"model": WeatherResponse, "description": "Успешный запрос"},
        400: {"model": ErrorResponse, "description": "Ошибка запроса"},
        404: {"model": ErrorResponse, "description": "Город не найден"}
    }
)
def get_weather(
    city: str = Path(..., description="Название города", example="Moscow"),
    units: str = Query("metric", description="Единицы измерения", regex="metric")
):
    """
    Получить текущую погоду для указанного города
    
    - city: Название города, например: Moscow, Astana
    - units: Система единиц
    """
    try:
        weather_data = get_weather_data(city)
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения данных: {str(e)}")

@app.get(
    "/api/v1/weather/",
    response_model=List[WeatherResponse],
    responses={
        200: {"model": List[WeatherResponse], "description": "Успешный запрос"},
        400: {"model": ErrorResponse, "description": "Ошибка запроса"}
    }
)
def get_weather_multiple_cities(
    cities: str = Query(..., description="Список городов через запятую", example="Moscow,Perm,Pskov")
):
    """
    Получить погоду для нескольких городов одновременно
    cities - Список городов через запятую
    """
    try:
        city_list = [city.strip() for city in cities.split(",")]
        weather_data = []
        
        for city in city_list:
            try:
                data = get_weather_data(city)
                weather_data.append(data)
            except Exception as e:
                # Пропускаем города с ошибками
                continue
        
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения данных: {str(e)}")

@app.get("/api/v1/health", include_in_schema=True)
def health_check():
    """
    Проверка здоровья API
    """
    return {"status": "healthy", "service": "Weather API"}

# Обработчики ошибок


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint не найден"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"}
    )