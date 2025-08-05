import logging
import time
import sys
from datetime import datetime
from threading import Event
import csv

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.log import LogConfig
from cflib.positioning.motion_commander import MotionCommander

URI = 'radio://0/80/2M'
DEFAULT_HEIGHT = 0.5
POSITION_TOLERANCE = 0.05  # meters

deck_attached_event = Event()
current_position = {'x': 0.0, 'y': 0.0}

#globals that affect what is being logged to csv
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"velocity_data/log_velocity_{timestamp}.csv"

# log RPM
"""
LOG_VARS = [
('motor.m1', 'uint16_t'),
('motor.m2', 'uint16_t'),
('motor.m3', 'uint16_t'),
('motor.m4', 'uint16_t')
]
"""
#log higher level control
"""
LOG_VARS = [
('stabilizer.roll', 'float'),
('stabilizer.pitch', 'float'),
('stabilizer.yaw', 'float'),
('stabilizer.thrust', 'float')
]
"""

#log velocities for flow deck
LOG_VARS = [
('stateEstimate.vx', 'float'),
('stateEstimate.vy', 'float'),
('stateEstimate.vz', 'float'),
('stateEstimate.roll', 'float')
]

#end of csv logged globals

def param_deck_attached(name, value_str):
    if int(value_str) == 1:
        deck_attached_event.set()



def create_csv_and_logConfig():
    #returns logConfig, csv_file
    csv_file = open(csv_filename, "w", newline='')

    writer = csv.writer(csv_file)
    writer.writerow(['Time (ms)', 'roll', 'pitch', 'yaw', 'thrust'])

    log_config = LogConfig(name='Logging', period_in_ms=100)

    #######
    #This section is necessary for waypoints!
    log_config.add_variable('stateEstimate.x', 'float')
    log_config.add_variable('stateEstimate.y', 'float')
    ######

    for var, var_type in LOG_VARS:
        log_config.add_variable(var, var_type)


    start_time = time.time()

    def log_callback(timestamp, data, _):
        #######
        #This section is necessary for waypoints!
        current_position['x'] = data['stateEstimate.x']
        current_position['y'] = data['stateEstimate.y']
        #######
        
        row = [time.time()-start_time] + [data[log_var[0]] for log_var in LOG_VARS]
        print(row)
        writer.writerow(row)

    def log_error_callback(_log_conf, msg):
        print("Log error:", msg)

    log_config.data_received_cb.add_callback(log_callback)
    log_config.error_cb.add_callback(log_error_callback)

    return log_config, csv_file



def move_to_position(mc, target_x, target_y, timeout=10.0):
    start_time = time.time()
    while time.time() - start_time < timeout:
        dx = target_x - current_position['x']
        dy = target_y - current_position['y']

        if abs(dx) < POSITION_TOLERANCE and abs(dy) < POSITION_TOLERANCE:
            break

        vx = max(min(dx, 0.2), -0.2)
        vy = max(min(dy, 0.2), -0.2)
        mc.start_linear_motion(vx, vy, 0)
        time.sleep(0.1)

    mc.stop()

def fly_square(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        print("Taking off...")
        time.sleep(2.0)

        # Reset estimated position to (0, 0)
        scf.cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.1)
        scf.cf.param.set_value('kalman.resetEstimation', '0')
        time.sleep(2.0)

        # Move in a 1-meter square (clockwise)
        move_to_position(mc, 1.0, 0.0)
        move_to_position(mc, 1.0, 1.0)
        move_to_position(mc, 0.0, 1.0)
        move_to_position(mc, 0.0, 0.0)

        print("Landing...")

def t1_t4(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        print("Taking off...")
        time.sleep(2.0)

        # Reset estimated position to (0, 0)
        scf.cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.1)
        scf.cf.param.set_value('kalman.resetEstimation', '0')
        time.sleep(2.0)

        move_to_position(mc, 1.0, -1.0)

        print("Landing...")

def take_off_simple(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        print("Taking off and hovering...")
        time.sleep(3)  # Hover for 3 seconds
        mc.stop()
        print("Landing...")


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)

    cflib.crtp.init_drivers()
    cf = Crazyflie(rw_cache='./cache')
    cf.param.add_update_callback(group='deck', name='bcFlow2', cb=param_deck_attached)

    print("Connecting...")

    with SyncCrazyflie(URI, cf=cf) as scf:
        if not deck_attached_event.wait(timeout=5):
            print("No flow deck detected!")
            sys.exit(1)

        log_conf,csv_file = create_csv_and_logConfig()


        scf.cf.log.add_config(log_conf)
        log_conf.start()

        # Arm the drone
        scf.cf.platform.send_arming_request(True)
        time.sleep(1.0)

        #fly_square(scf)
        #take_off_simple(scf)
        t1_t4(scf)

        log_conf.stop()
        csv_file.close()
        print(f"data saved to {csv_filename}")