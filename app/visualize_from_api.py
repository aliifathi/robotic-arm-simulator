from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import math

from app.kinematics import inverse_kinematics

app = FastAPI()

# Set up static and template directories
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Pydantic model for API
class Point(BaseModel):
    x: float
    y: float

# API route: returns joint angles for a given (x, y)
@app.post("/ik")
def calculate_angles(point: Point):
    theta1, theta2 = inverse_kinematics(point.x, point.y)
    return {"theta1": theta1, "theta2": theta2}

# Root route: shows input form
@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# Optional: if you want to process form submission and return result
@app.post("/ik", response_class=HTMLResponse)
async def handle_form(request: Request, x: float = Form(...), y: float = Form(...)):
    theta1, theta2 = inverse_kinematics(x, y)
    return templates.TemplateResponse("form.html", {
        "request": request,
        "theta1": round(theta1, 2),
        "theta2": round(theta2, 2),
        "x": x,
        "y": y
    })
