import time
import csv
from datetime import datetime
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig

# Init drivers
cflib.crtp.init_drivers()

uri = 'radio://0/80/2M'
cf = Crazyflie()

# File setup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"log_{timestamp}.csv"
csv_file = open(csv_filename, mode='w', newline='')
writer = csv.writer(csv_file)
writer.writerow(['Time (ms)', 'Battery (V)', 'Roll (°)', 'Pitch (°)', 'Yaw (°)'])

# This will be set after logging starts
log_config = None
start_time = None

def log_callback(timestamp, data, logconf):
    global start_time
    if start_time is None:
        start_time = time.time()

    row = [
        timestamp,
        data['pm.vbat'],
        data['stabilizer.roll'],
        data['stabilizer.pitch'],
        data['stabilizer.yaw']
    ]
    print(f"{row}")
    writer.writerow(row)

    # Stop logging after 10 seconds
    if time.time() - start_time > 10:
        print("Stopping log...")
        logconf.stop()
        csv_file.close()
        print(f"Log saved to {csv_filename}")
        cf.close_link()

def connected(link_uri):
    global log_config
    print("Connected – starting log")
    log_config = LogConfig(name='Log', period_in_ms=100)
    log_config.add_variable('pm.vbat', 'float')
    log_config.add_variable('stabilizer.roll', 'float')
    log_config.add_variable('stabilizer.pitch', 'float')
    log_config.add_variable('stabilizer.yaw', 'float')

    cf.log.add_config(log_config)
    log_config.data_received_cb.add_callback(log_callback)
    log_config.start()
    print("Logging...")

def connection_failed(link_uri, msg): print("Failed:", msg)
def connection_lost(link_uri, msg): print("Lost:", msg)

cf.connected.add_callback(connected)
cf.connection_failed.add_callback(connection_failed)
cf.connection_lost.add_callback(connection_lost)

print("Connecting...")
cf.open_link(uri)

# Block until disconnected
while cf.is_connected():
    time.sleep(0.1)