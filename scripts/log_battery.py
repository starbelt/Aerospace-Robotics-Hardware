import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig

# Initialize drivers
cflib.crtp.init_drivers()

uri = 'radio://0/80/2M'
cf = Crazyflie()

def log_callback(timestamp, data, logconf):
    print(f"[{timestamp}] Battery voltage: {data['pm.vbat']} V")

def connected(link_uri):
    print("Connected, setting up logging...")
    
    log_config = LogConfig(name='Battery', period_in_ms=1000)  # Log every 1 sec
    log_config.add_variable('pm.vbat', 'float')  # Battery voltage
    
    cf.log.add_config(log_config)
    log_config.data_received_cb.add_callback(log_callback)
    log_config.start()

def connection_failed(link_uri, msg):
    print(f"Connection failed: {msg}")

def connection_lost(link_uri, msg):
    print(f"Connection lost: {msg}")

cf.connected.add_callback(connected)
cf.connection_failed.add_callback(connection_failed)
cf.connection_lost.add_callback(connection_lost)

print("Connecting...")
cf.open_link(uri)

# Keep the script alive to receive logs
while True:
    time.sleep(1)