import logging
import time
import sys
from threading import Event

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

def param_deck_attached(name, value_str):
    if int(value_str) == 1:
        deck_attached_event.set()

def position_est_cb(timestamp, data, logconf):
    current_position['x'] = data['stateEstimate.x']
    current_position['y'] = data['stateEstimate.y']

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
        move_to_position(mc, 2.0, 0.0)
        move_to_position(mc, 2.0, 2.0)
        move_to_position(mc, 0.0, 2.0)
        move_to_position(mc, 0.0, 0.0)

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

        # Set up position logging
        log_conf = LogConfig(name='Position', period_in_ms=100)
        log_conf.add_variable('stateEstimate.x', 'float')
        log_conf.add_variable('stateEstimate.y', 'float')

        scf.cf.log.add_config(log_conf)
        log_conf.data_received_cb.add_callback(position_est_cb)
        log_conf.start()

        # Arm the drone
        scf.cf.platform.send_arming_request(True)
        time.sleep(1.0)

        fly_square(scf)

        log_conf.stop()