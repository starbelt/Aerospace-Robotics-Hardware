import sys
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# initialize script arguments
data_file = ''

# parse script arguments
if len(sys.argv)==2:
    data_file = sys.argv[1]
else:
    print('Usage: python3 script_name.py data_file')
    exit()

# Load the CSV file using the full path
df = pd.read_csv(data_file, skiprows=5)

# Extract the Time, Position X, Y, and Z columns
df_xyz = df[['Unnamed: 1', 'Position', 'Position.1', 'Position.2']].copy()
df_xyz.columns = ['Time (s)', 'Position X', 'Position Y', 'Position Z']

# Clean the data: drop missing and non-numeric values
df_xyz = df_xyz.dropna()
df_xyz = df_xyz[pd.to_numeric(df_xyz['Time (s)'], errors='coerce').notnull()]
df_xyz = df_xyz[pd.to_numeric(df_xyz['Position X'], errors='coerce').notnull()]
df_xyz = df_xyz[pd.to_numeric(df_xyz['Position Y'], errors='coerce').notnull()]
df_xyz = df_xyz[pd.to_numeric(df_xyz['Position Z'], errors='coerce').notnull()]
df_xyz = df_xyz.astype(float)

# 3D Plot
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
ax.plot(df_xyz['Position X'], df_xyz['Position Y'], df_xyz['Position Z'], marker='o', markersize=2,linestyle='None')

ax.set_xlabel('Position X (m)')
ax.set_ylabel('Position Y (m)')
ax.set_zlabel('Position Z (m)')
ax.set_title('3D Flight Path')
plt.tight_layout()
plt.show()
