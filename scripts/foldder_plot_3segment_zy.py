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

        # Clean and extract X/Y for 3 segments
        segment1 = df[['Position', 'Position.2']].copy()
        segment2 = df[['Position.15', 'Position.17']].copy()
        segment3 = df[['Position', 'Position.2']].copy()

        segment1 = segment1.apply(pd.to_numeric, errors='coerce').dropna()
        segment2 = segment2.apply(pd.to_numeric, errors='coerce').dropna()
        segment3 = segment3.apply(pd.to_numeric, errors='coerce').dropna()

        # Plot
        plt.plot(segment1['Position'], segment1['Position.2'], label=f'{file}', marker='o', markersize=.5, linestyle='--')
        plt.plot(segment2['Position.15'], segment2['Position.17'], marker='o', markersize=.5, linestyle='--')
        plt.plot(segment3['Position'], segment3['Position.2'], marker='o', markersize=.5, linestyle='--')

    except Exception as e:
        print(f"Skipping {file}: {e}")

# Finalize plot
plt.xlabel('Position x (cm)')
plt.ylabel('Position z (cm)')
plt.title('2D Trajectory of Crazyflie')
plt.grid(True)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)  # Legend to the right

plt.xlim(-150, 50)   # Adjust these as needed
plt.ylim(-50, 200)  

plt.tight_layout()

# Save as PDF
plt.savefig("C:/Users/Rikar/git-repos/Aerospace-Robotics-Hardware/plots/plot2.pdf",
            format='pdf', bbox_inches='tight', dpi=300)

plt.show()