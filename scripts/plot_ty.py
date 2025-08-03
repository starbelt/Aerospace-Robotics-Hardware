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

# Extract the Time and Position Y columns
df_ty = df[['Unnamed: 1', 'Position.1']].copy()
df_ty.columns = ['Time (s)', 'Position Y']

# Clean the data: drop missing and non-numeric values
df_ty = df_ty.dropna()
df_ty = df_ty[pd.to_numeric(df_ty['Time (s)'], errors='coerce').notnull()]
df_ty = df_ty[pd.to_numeric(df_ty['Position Y'], errors='coerce').notnull()]
df_ty = df_ty.astype(float)

# Plotting Time vs Y
plt.figure(figsize=(8, 6))
plt.plot(df_ty['Time (s)'], df_ty['Position Y'], marker='o', markersize=2, linestyle='None')
plt.xlabel('Time (seconds)')
plt.ylabel('Position Y (meters)')
plt.title('Flight Altitude Over Time')
plt.grid(True)
plt.tight_layout()

plt.savefig("C:/Users/Rikar/git-repos/Aerospace-Robotics-Hardware/plots/plot.pdf", format='pdf', bbox_inches='tight', dpi=300)

plt.show()
