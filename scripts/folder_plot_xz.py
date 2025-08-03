import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

if len(sys.argv) != 2:
    sys.exit()

folder_path = sys.argv[1]

# Get all .csv files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Setup colormap
colors = plt.cm.get_cmap('tab10', len(csv_files))

# Create plot
plt.figure(figsize=(12, 6))

for i, file in enumerate(csv_files):
    file_path = os.path.join(folder_path, file)

    try:
        df = pd.read_csv(file_path, skiprows=5)
        df_xz = df[['Unnamed: 1', 'Position', 'Position.2']].copy()
        df_xz.columns = ['Time (s)', 'Position X', 'Position Z']

        df_xz = df_xz.dropna()
        df_xz = df_xz[
            pd.to_numeric(df_xz['Time (s)'], errors='coerce').notnull() &
            pd.to_numeric(df_xz['Position X'], errors='coerce').notnull() &
            pd.to_numeric(df_xz['Position Z'], errors='coerce').notnull()
        ].astype(float)

        plt.plot(df_xz['Position X'], df_xz['Position Z'],
                 marker='o', markersize=2, linestyle='None',
                 label=file, color=colors(i))

    except Exception as e:
        print(f"Skipping {file}: {e}")

# Finish plot
plt.xlabel('Position X (m)')
plt.ylabel('Position Z (m)')
plt.title('2D Flight Paths (X vs Z)')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)  # Legend to the right
plt.axis('equal')
plt.grid(True)
plt.tight_layout()

plt.savefig("C:/Users/Rikar/git-repos/Aerospace-Robotics-Hardware/plots/plot.pdf", format='pdf', bbox_inches='tight', dpi=300)

plt.show()
