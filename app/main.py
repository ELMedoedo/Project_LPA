from fastapi import FastAPI, HTTPException
from .weather import get_weather_data

app = FastAPI(title="Weather API", description="Получение текущей температуры в городе")

@app.get("/weather/")
def get_weather(city: str):
    """
    Получить текущую температуру в городе
    
    - **city**: Название города (например: Moscow, London, Paris)
    """
    try:
        weather_data = get_weather_data(city)
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения данных: {str(e)}")

@app.get("/")
def read_root():
    return {"/weather/?city=Город на англ"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)