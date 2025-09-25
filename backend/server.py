from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from joblib import load
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

app.mount("/images", StaticFiles(directory="images"), name="images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WeatherRequest(BaseModel):
    region: str
    model: str
    lead_time: float
    time_scale: str
    month: str


class StatsRequest(BaseModel):
    lat: float
    lng: float

@app.post("/submit")
async def run_script(data: WeatherRequest):
    try:
        result = subprocess.run(
            [
                "python", "script.py",
                data.region,
                data.model,
                str(data.lead_time),
                data.time_scale,
                data.month
            ],
            capture_output=True,
            text=True,
            check=True
        )

        # Capture plots from stdout
        plot_paths = []
        for line in result.stdout.splitlines():
            if line.startswith("::PLOT::"):
                abs_path = line.replace("::PLOT::", "").strip()
                filename = os.path.basename(abs_path)
                plot_paths.append(f"/images/{filename}")

        return {
            "success": True,
            "stdout": result.stdout,
            "plots": plot_paths
        }

    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": e.stderr,
            "returncode": e.returncode
        }

@app.post("/stats")
async def get_stats(indices: StatsRequest):
    data = load("./cache/mac/CanCM4i_lead0.5_metrics.joblib")
    data = data['Jan']

    res = {}

    for key, val in data.items():
        if key == "lead":
            continue
        if key in ("drought_f1", "flood_f1"):
            res[key] = str(val)
        else:
            try:
                selected_val = val.sel(y=indices.lat, x=indices.lng, method="nearest").compute().item()
                res[key] = f"{selected_val:.3f}"
            except Exception as e:
                res[key] = "n/a"

    return res