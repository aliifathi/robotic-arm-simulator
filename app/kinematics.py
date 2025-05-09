# app/kinematics.py
import math

def inverse_kinematics(x, y, L1=100, L2=100):
    distance = math.sqrt(x**2 + y**2)

    # Check if the point is reachable
    if distance > (L1 + L2):
        return None, None  # unreachable

    # Calculate the angle for the elbow
    cos_theta2 = (x**2 + y**2 - L1**2 - L2**2) / (2 * L1 * L2)
    theta2 = math.acos(cos_theta2)

    # Calculate the angle for the shoulder
    k1 = L1 + L2 * math.cos(theta2)
    k2 = L2 * math.sin(theta2)
    theta1 = math.atan2(y, x) - math.atan2(k2, k1)

    # Convert to degrees (optional, easier for visualization)
    theta1_deg = math.degrees(theta1)
    theta2_deg = math.degrees(theta2)

    return theta1_deg, theta2_deg
