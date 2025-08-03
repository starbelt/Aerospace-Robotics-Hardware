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
        df_ty = df[['Unnamed: 1', 'Position.1']].copy()
        df_ty.columns = ['Time (s)', 'Position Y']

        df_ty = df_ty.dropna()
        df_ty = df_ty[
            pd.to_numeric(df_ty['Time (s)'], errors='coerce').notnull() &
            pd.to_numeric(df_ty['Position Y'], errors='coerce').notnull()
        ].astype(float)

        plt.plot(df_ty['Time (s)'], df_ty['Position Y'],
                 marker='o', markersize=2, linestyle='None',
                 label=file, color=colors(i))

    except Exception as e:
        print(f"Skipping {file}: {e}")

# Finish plot
plt.xlabel('Time (s)')
plt.ylabel('Position Y (m)')
plt.title('Flight Altitude Over Time')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)  # Legend to the right
plt.grid(True)
plt.tight_layout()

plt.savefig("C:/Users/Rikar/git-repos/Aerospace-Robotics-Hardware/plots/plot.pdf",
            format='pdf', bbox_inches='tight', dpi=300)
plt.show()
