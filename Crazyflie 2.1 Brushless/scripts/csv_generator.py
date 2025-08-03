import csv

# === CONFIGURATION ===
# List of movements: direction and distance (in meters)
movements = [
    ('x', +1),
    ('y', +1),
]

output_file = 'generated_path.csv'
speed = 1.0  # m/s constant speed
start_pos = [0.0, 0.0, 0.4]  # starting (x, y, z)
yaw = 0.0  # constant yaw in radians

# === GENERATE WAYPOINTS ===
waypoints = []
current_pos = start_pos[:]
time = 0.0

waypoints.append([time, *current_pos, yaw])

for axis, distance in movements:
    idx = {'x': 0, 'y': 1, 'z': 2}[axis.lower()]
    current_pos[idx] += distance
    time += abs(distance) / speed
    waypoints.append([time, *current_pos, yaw])

# === SAVE TO CSV ===
with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['time', 'x', 'y', 'z', 'yaw'])
    writer.writerows(waypoints)

print(f"CSV saved to: {output_file}")
