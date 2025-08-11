import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python plot_xz.py path_to_csv_folder")
        sys.exit(1)

    folder_path = sys.argv[1]

    # Get all .csv files in the folder
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found in the specified folder.")
        sys.exit(1)

    # Generate distinct colors
    cmap = plt.cm.get_cmap('hsv')
    colors = [cmap(i / len(csv_files)) for i in range(len(csv_files))]

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
                     marker='o', markersize=0.5, linestyle='--',
                     label=file, color=colors[i])

        except Exception as e:
            print(f"Skipping {file}: {e}")

    # Finalize plot
    plt.xlabel('Position X (cm)')
    plt.ylabel('Position Z (cm)')
    plt.title('2D Flight Paths (X vs Z)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    plt.axis('equal')
    plt.grid(True)
    plt.tight_layout()

    # Save figure with timestamp
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = f"plot_{timestamp}.pdf"
    output_path = os.path.join("C:/Users/Rikar/git-repos/Aerospace-Robotics-Hardware/plots", output_file)
    plt.savefig(output_path, format='pdf', bbox_inches='tight', dpi=300)

    print(f"Plot saved as {output_path}")
    plt.show()
