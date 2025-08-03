import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig

# Init drivers
cflib.crtp.init_drivers()

uri = 'radio://0/80/2M'
cf = Crazyflie()

def log_callback(timestamp, data, logconf):
    print(f"[{timestamp}] vbat: {data['pm.vbat']:.2f} V | roll: {data['stabilizer.roll']:.2f}° | pitch: {data['stabilizer.pitch']:.2f}° | yaw: {data['stabilizer.yaw']:.2f}°")

def connected(link_uri):
    print("Connected, setting up attitude logging...")

    log_config = LogConfig(name='Attitude', period_in_ms=500)
    log_config.add_variable('pm.vbat', 'float')
    log_config.add_variable('stabilizer.roll', 'float')
    log_config.add_variable('stabilizer.pitch', 'float')
    log_config.add_variable('stabilizer.yaw', 'float')

    cf.log.add_config(log_config)
    log_config.data_received_cb.add_callback(log_callback)
    log_config.start()

def connection_failed(link_uri, msg):
    print("Connection failed:", msg)

def connection_lost(link_uri, msg):
    print("Connection lost:", msg)

cf.connected.add_callback(connected)
cf.connection_failed.add_callback(connection_failed)
cf.connection_lost.add_callback(connection_lost)

print("Connecting...")
cf.open_link(uri)

while True:
    time.sleep(1)
