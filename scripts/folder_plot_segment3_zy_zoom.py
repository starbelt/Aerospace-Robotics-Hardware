import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

# Check for proper usage
if len(sys.argv) != 2:
    print("Usage: python plot_body1_skip10.py path_to_folder")
    sys.exit()

folder_path = sys.argv[1]
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
csv_files.sort()

plt.figure(figsize=(10, 8))

for file in csv_files:
    try:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path, skiprows=5)

        # Extract segment3 Z and Y
        segment3 = df[['Position.32', 'Position.31']].copy()
        segment3 = segment3.apply(pd.to_numeric, errors='coerce').dropna()

        # Skip every 10th point
        segment3 = segment3.reset_index(drop=True)
        segment3 = segment3.drop(segment3.index[::10])

        # Plot
        plt.plot(segment3['Position.32'], segment3['Position.31'],
                 marker='o', markersize=.5, linestyle='--', linewidth=.5, label=f'{file} - segment 3')

    except Exception as e:
        print(f"Skipping {file}: {e}")

# Finalize plot
plt.xlabel('Position Z (mm)')
plt.ylabel('Position Y (mm)')
plt.title('2D Trajectory of Follower Arm Segment 3')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)  # Legend to the right
plt.axis('equal')
plt.grid(True)
plt.tight_layout()

# Save as PDF
plt.savefig("C:/Users/Rikar/git-repos/Aerospace-Robotics-Hardware/plots/plot.pdf",
            format='pdf', bbox_inches='tight', dpi=300)

plt.xlim(550, 600)
plt.ylim(750, 950)

plt.show()
