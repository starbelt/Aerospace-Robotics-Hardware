import logging
import time
import sys
from threading import Event

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

URI = 'radio://0/80/2M'

# Default height for takeoff
DEFAULT_HEIGHT = 0.5

# For detecting the Flow deck (optional but safe)
deck_attached_event = Event()

def param_deck_attached(name, value_str):
    if int(value_str) == 1:
        deck_attached_event.set()

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

        # Arm the Crazyflie
        scf.cf.platform.send_arming_request(True)
        time.sleep(1.0)

        take_off_simple(scf)
