import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

if len(sys.argv) != 2:
    print("Usage: python plot_3body_folder.py path_to_folder")
    sys.exit()

folder_path = sys.argv[1]
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

plt.figure(figsize=(10, 8))

for file in csv_files:
    try:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path, skiprows=5)

        # Clean and extract X/Z for 3 segments
        segment1 = df[['Position', 'Position.2']].copy()
        segment2 = df[['Position.15', 'Position.17']].copy()
        segment3 = df[['Position', 'Position.2']].copy()

        segment1 = segment1.apply(pd.to_numeric, errors='coerce').dropna()
        segment2 = segment2.apply(pd.to_numeric, errors='coerce').dropna()
        segment3 = segment3.apply(pd.to_numeric, errors='coerce').dropna()

        #  Extract traj number from filename
        traj_num = int(''.join(filter(str.isdigit, file.replace('crazyflie_traj', '').replace('.csv', ''))))
        color = 'red' if traj_num <= 6 else 'blue'

        plt.plot(segment1['Position'], segment1['Position.2'],
                 label=f'{file}', marker='o', markersize=0.5,
                 linestyle='--', color=color)

    except Exception as e:
        print(f"Skipping {file}: {e}")

# Finalize plot
plt.xlabel('Position x (cm)')
plt.ylabel('Position z (cm)')
plt.title('2D Trajectory of Crazyflie')
plt.grid(True)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
plt.xlim(-200, 50)
plt.ylim(-50, 200)
plt.tight_layout()
plt.show()
