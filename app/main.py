from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import time
from datetime import datetime

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
    start = time.time()
    try:
        theta1, theta2 = inverse_kinematics(point.x, point.y)
        success = True
    except Exception:
        theta1 = theta2 = 0
        success = False
    end = time.time()
    exec_time = round((end - start) * 1000, 2)
    timestamp = datetime.now().isoformat()
    error = calculate_distance_error(point.x, point.y, theta1, theta2)
    log_result(point.x, point.y, theta1, theta2, success, timestamp, "API", exec_time, error)
    return {
        "theta1": theta1,
        "theta2": theta2,
        "success": success,
        "timestamp": timestamp,
        "source": "API",
        "exec_time_ms": exec_time,
        "error": error
    }

# HTML form page
@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# Form submission handler with visualization
@app.post("/ik", response_class=HTMLResponse)
async def handle_form(request: Request, x: float = Form(...), y: float = Form(...)):
    start = time.time()
    try:
        theta1, theta2 = inverse_kinematics(x, y)
        success = True
    except Exception:
        theta1 = theta2 = 0
        success = False
    end = time.time()

    exec_time = round((end - start) * 1000, 2)
    timestamp = datetime.now().isoformat()
    error = calculate_distance_error(x, y, theta1, theta2)
    source = "Form"

    log_result(x, y, theta1, theta2, success, timestamp, source, exec_time, error)

    # Arm segment lengths
    L1 = L2 = 100
    theta1_rad = np.radians(theta1)
    theta2_rad = np.radians(theta2)

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
        "success": success,
        "exec_time": exec_time,
        "timestamp": timestamp,
        "source": source,
        "error": error,
        "image_url": "/static/arm_plot.png"
    })

# Logger to save results in CSV file
def log_result(x, y, theta1, theta2, success, timestamp, source, exec_time, error):
    log_file = "results.csv"
    file_exists = os.path.isfile(log_file)
    with open(log_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["X", "Y", "Theta1", "Theta2", "Success", "Timestamp", "Source", "ExecutionTime(ms)", "DistanceError"])
        writer.writerow([x, y, round(theta1, 2), round(theta2, 2), success, timestamp, source, exec_time, error])

# Compute distance between actual end-effector and target
def calculate_distance_error(x, y, theta1, theta2):
    L1 = L2 = 100
    theta1_rad = np.radians(theta1)
    theta2_rad = np.radians(theta2)
    joint1_x = L1 * np.cos(theta1_rad)
    joint1_y = L1 * np.sin(theta1_rad)
    end_effector_x = joint1_x + L2 * np.cos(theta1_rad + theta2_rad)
    end_effector_y = joint1_y + L2 * np.sin(theta1_rad + theta2_rad)
    error = np.sqrt((x - end_effector_x)**2 + (y - end_effector_y)**2)
    return round(error, 2)


# Route to render 3D simulation view
@app.get("/view-3d", response_class=HTMLResponse)
async def view_3d_page(request: Request):
    return templates.TemplateResponse("form_3d.html", {"request": request})

