from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import matplotlib.pyplot as plt
import numpy as np
import os

from app.kinematics import inverse_kinematics

app = FastAPI()

# Setup static and template folders
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Pydantic model for API JSON endpoint
class Point(BaseModel):
    x: float
    y: float

# JSON-based API for programmatic access
@app.post("/api/ik")
def calculate_angles_json(point: Point):
    theta1, theta2 = inverse_kinematics(point.x, point.y)
    return {"theta1": theta1, "theta2": theta2}

# HTML form page
@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# Form submission handler with visualization
@app.post("/ik", response_class=HTMLResponse)
async def handle_form(request: Request, x: float = Form(...), y: float = Form(...)):
    theta1, theta2 = inverse_kinematics(x, y)

    # Arm segment lengths
    L1 = L2 = 100

    # Convert angles to radians
    theta1_rad = np.radians(theta1)
    theta2_rad = np.radians(theta2)

    # Joint positions
    joint1 = (L1 * np.cos(theta1_rad), L1 * np.sin(theta1_rad))
    joint2 = (
        joint1[0] + L2 * np.cos(theta1_rad + theta2_rad),
        joint1[1] + L2 * np.sin(theta1_rad + theta2_rad)
    )

    # Plot and save image
    fig, ax = plt.subplots()
    ax.plot([0, joint1[0], joint2[0]], [0, joint1[1], joint2[1]], marker='o', linewidth=4)
    ax.scatter(x, y, color='red', label='Target')
    ax.set_title("Robotic Arm Visualization")
    ax.axis('equal')
    ax.grid(True)
    ax.legend()

    os.makedirs("app/static", exist_ok=True)
    image_path = "app/static/arm_plot.png"
    plt.savefig(image_path)
    plt.close()

    return templates.TemplateResponse("form.html", {
        "request": request,
        "theta1": round(theta1, 2),
        "theta2": round(theta2, 2),
        "x": x,
        "y": y,
        "image_url": "/static/arm_plot.png"
    })
