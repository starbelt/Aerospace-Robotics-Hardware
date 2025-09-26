import sys
import pandas as pd
import matplotlib.pyplot as plt

# initialize script arguments
data_file = ''

# parse script arguments
if len(sys.argv)==2:
  data_file = sys.argv[1]
else:
  print(\
   'Usage: '\
   'python3 script_name.py data_file'\
  )
  exit()

# Load the CSV file using the full path
df = pd.read_csv(data_file, skiprows=5)

# Extract the Time, Position X, and Position Z columns
df_xy = df[['Unnamed: 1', 'Position.2', 'Position']].copy()
df_xz.columns = ['Time (s)', 'Position X', 'Position Z']

# Clean the data: drop missing and non-numeric values
df_xz = df_xz.dropna()
df_xz = df_xz[pd.to_numeric(df_xz['Time (s)'], errors='coerce').notnull()]
df_xz = df_xz[pd.to_numeric(df_xz['Position X'], errors='coerce').notnull()]
df_xz = df_xz[pd.to_numeric(df_xz['Position Z'], errors='coerce').notnull()]
df_xz = df_xz.astype(float)

# Plotting X vs Z
plt.figure(figsize=(8, 6))
plt.plot(df_xz['Position X'], df_xz['Position Z'], marker='o', markersize=2, linestyle='None')
plt.xlabel('Position X (meters)')
plt.ylabel('Position Z (meters)')
plt.title('2D Flight Path (X vs Z)')
plt.grid(True)
plt.axis('equal')  # keeps aspect ratio square
plt.tight_layout()

plt.savefig("C:/Users/Rikar/git-repos/Aerospace-Robotics-Hardware/plots/plot.pdf", format='pdf', bbox_inches='tight', dpi=300)

plt.show()

