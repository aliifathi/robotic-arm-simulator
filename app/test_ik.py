import matplotlib.pyplot as plt
import numpy as np

# Arm configuration
L1 = 100
L2 = 100
x_target, y_target = 150, 50

# Inverse Kinematics function (already exists)
from kinematics import inverse_kinematics

theta1, theta2 = inverse_kinematics(x_target, y_target)

# Convert angles to radians
theta1_rad = np.radians(theta1)
theta2_rad = np.radians(theta2)

# Joint positions
x0, y0 = 0, 0  # Base
x1 = L1 * np.cos(theta1_rad)
y1 = L1 * np.sin(theta1_rad)
x2 = x1 + L2 * np.cos(theta1_rad + theta2_rad)
y2 = y1 + L2 * np.sin(theta1_rad + theta2_rad)

# Plotting
plt.figure(figsize=(6, 6))
plt.plot([x0, x1, x2], [y0, y1, y2], '-o', linewidth=3)
plt.plot(x_target, y_target, 'rx', markersize=10, label='Target')
plt.xlim(-200, 200)
plt.ylim(-200, 200)
plt.grid(True)
plt.gca().set_aspect('equal', adjustable='box')
plt.title("2D Robotic Arm Simulation")
plt.legend()
plt.show()
