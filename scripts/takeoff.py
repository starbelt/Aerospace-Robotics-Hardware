import time
import csv
import logging
from datetime import datetime

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.log import LogConfig

# Setup
URI = 'radio://0/80/2M'
LOG_DURATION = 10  # seconds

# Timestamp for CSV
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"log_{timestamp}.csv"

# Variables to log
LOG_VARS = [
    ('pm.vbat', 'float'),
    ('stabilizer.roll', 'float'),
    ('stabilizer.pitch', 'float'),
    ('stabilizer.yaw', 'float')
]

# Logging setup
logging.basicConfig(level=logging.ERROR)
cflib.crtp.init_drivers()


def log_and_save(scf):
    with open(csv_filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Time (ms)', 'Battery (V)', 'Roll (°)', 'Pitch (°)', 'Yaw (°)'])

        log_config = LogConfig(name='Logging', period_in_ms=100)
        for var, var_type in LOG_VARS:
            log_config.add_variable(var, var_type)

        start_time = time.time()

        def log_callback(timestamp, data, _):
            row = [
                timestamp,
                data['pm.vbat'],
                data['stabilizer.roll'],
                data['stabilizer.pitch'],
                data['stabilizer.yaw']
            ]
            print(row)
            writer.writerow(row)

        def log_error_callback(_log_conf, msg):
            print("Log error:", msg)

        log_config.data_received_cb.add_callback(log_callback)
        log_config.error_cb.add_callback(log_error_callback)

        scf.cf.log.add_config(log_config)
        log_config.start()
        print("Logging started...")

        # Wait for logging duration
        while time.time() - start_time < LOG_DURATION:
            time.sleep(0.1)

        log_config.stop()
        print(f"Logging stopped. Data saved to {csv_filename}")


if __name__ == '__main__':
    print("Connecting to Crazyflie...")
    cf = Crazyflie(rw_cache='./cache')

    with SyncCrazyflie(URI, cf=cf) as scf:
        log_and_save(scf)