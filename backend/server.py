from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class WeatherRequest(BaseModel):
    region: str
    model: str
    lead_time: str
    time_scale: str

@app.post("/submit")
async def submit_weather(data: WeatherRequest):
    # You can add processing logic here
    return {
        "message": "Data received successfully",
        "data": data.dict()
    }
