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

        # Extract segment2 Z and Y
        segment2 = df[['Position.17', 'Position.16']].copy()
        segment2 = segment2.apply(pd.to_numeric, errors='coerce').dropna()

        # Skip every 10th point
        segment2 = segment2.reset_index(drop=True)
        segment2 = segment2.drop(segment2.index[::10])

        # Plot
        plt.plot(segment2['Position.17'], segment2['Position.16'],
                 marker='o', markersize=.5, linestyle='none', label=f'{file} - segment 2')

    except Exception as e:
        print(f"Skipping {file}: {e}")

# Finalize plot
plt.xlabel('Position Z (mm)')
plt.ylabel('Position Y (mm)')
plt.title('2D Trajectory of Follower Arm Segment 2')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)  # Legend to the right
plt.axis('equal')
plt.grid(True)
plt.tight_layout()

# Save as PDF
plt.savefig("C:/Users/Rikar/git-repos/Aerospace-Robotics-Hardware/plots/plot.pdf",
            format='pdf', bbox_inches='tight', dpi=300)

plt.show()
