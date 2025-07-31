import logging
import time
import sys
import numpy as np
from threading import Event

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.log import LogConfig
from cflib.positioning.motion_commander import MotionCommander

# ====== Config ======
URI = 'radio://0/80/2M'
DEFAULT_HEIGHT = 0.5

# ====== Globals ======
deck_attached_event = Event()
current_position = {'x': 0.0, 'y': 0.0}

# ====== Callbacks ======
def param_deck_attached(name, value_str):
    if int(value_str) == 1:
        deck_attached_event.set()

def position_est_cb(timestamp, data, logconf):
    current_position['x'] = data['stateEstimate.x']
    current_position['y'] = data['stateEstimate.y']

# ====== Coordinated Circle Flight ======
def fly_circle(scf, radius=1.0, forward_speed=0.3):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        print("Taking off...")
        time.sleep(2.0)

        # Reset position estimate
        scf.cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.1)
        scf.cf.param.set_value('kalman.resetEstimation', '0')
        time.sleep(2.0)

        # Yaw rate needed for a full circle
        angular_velocity = forward_speed / radius        # radians/sec
        yaw_rate_deg = np.degrees(angular_velocity)      # convert to degrees/sec

        # Time to complete one full circle
        circle_time = 2 * np.pi * radius / forward_speed
        dt = 0.1
        steps = int(circle_time / dt)

        for _ in range(steps):
            # Move forward in body frame and rotate
            mc.start_linear_motion(forward_speed, 0.0, 0.0, yaw_rate_deg)
            time.sleep(dt)

        mc.stop()
        print("Landing...")

# ====== Main ======
if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)

    cflib.crtp.init_drivers()
    cf = Crazyflie(rw_cache='./cache')

    cf.param.add_update_callback(group='deck', name='bcFlow2', cb=param_deck_attached)

    print("Connecting to Crazyflie...")

    with SyncCrazyflie(URI, cf=cf) as scf:
        if not deck_attached_event.wait(timeout=5):
            print("No flow deck detected!")
            sys.exit(1)

        # Set up logging (optional)
        log_conf = LogConfig(name='Position', period_in_ms=100)
        log_conf.add_variable('stateEstimate.x', 'float')
        log_conf.add_variable('stateEstimate.y', 'float')

        scf.cf.log.add_config(log_conf)
        log_conf.data_received_cb.add_callback(position_est_cb)
        log_conf.start()

        scf.cf.platform.send_arming_request(True)
        time.sleep(1.0)

        fly_circle(scf, radius=1.0, forward_speed=0.3)

        log_conf.stop()
