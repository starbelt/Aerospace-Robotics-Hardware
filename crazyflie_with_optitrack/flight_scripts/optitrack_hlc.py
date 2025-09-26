import time
from threading import Thread

import motioncapture
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.utils.reset_estimator import reset_estimator

uri = uri_helper.uri_from_env(default='radio://0/80/2M')
host_name = '172.30.224.1'
mocap_system_type = 'vrpn'
rigid_body_name = 'cf'
send_full_pose = True
orientation_std_dev = 8.0e-3

class MocapWrapper(Thread):
    def __init__(self, body_name):
        Thread.__init__(self)
        self.body_name = body_name
        self.on_pose = None
        self._stay_open = True
        self.start()

    def close(self):
        self._stay_open = False

    def run(self):
        mc = motioncapture.connect(mocap_system_type, {'hostname': host_name})
        while self._stay_open:
            mc.waitForNextFrame()
            for name, obj in mc.rigidBodies.items():
                if name == self.body_name and self.on_pose:
                    pos = obj.position
                    self.on_pose([pos[0], pos[1], pos[2], obj.rotation])

def send_extpose_quat(cf, x, y, z, quat):
    if send_full_pose:
        cf.extpos.send_extpose(x, y, z, quat.x, quat.y, quat.z, quat.w)
    else:
        cf.extpos.send_extpos(x, y, z)

def activate_kalman_estimator(cf):
    cf.param.set_value('stabilizer.estimator', '2')
    cf.param.set_value('locSrv.extQuatStdDev', orientation_std_dev)

def run_single_waypoint(cf):
    hl = cf.high_level_commander

    print("Taking off...")
    hl.takeoff(0.5, 2.0)
    time.sleep(3.0)

    print("Going to waypoint...")
    hl.go_to(0.0, 0.0, 0.5, 0, 3.0)  
    time.sleep(4.0)

    print("Landing...")
    hl.land(0.0, 2.0)
    time.sleep(3.0)

    hl.stop()

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    mocap_wrapper = MocapWrapper(rigid_body_name)

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        cf = scf.cf

        mocap_wrapper.on_pose = lambda pose: send_extpose_quat(cf, *pose[0:3], pose[3])
        activate_kalman_estimator(cf)
        reset_estimator(cf)

        cf.platform.send_arming_request(True)
        time.sleep(1.0)

        run_single_waypoint(cf)

    mocap_wrapper.close()