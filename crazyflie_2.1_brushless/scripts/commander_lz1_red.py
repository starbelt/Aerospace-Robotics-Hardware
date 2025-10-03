import time

import motioncapture
from threading import Thread 

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.utils.reset_estimator import reset_estimator
from cflib.positioning.motion_commander import MotionCommander

# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/78/1M/E7E7E7E7E6')

# The host name or ip address of the mocap system
host_name = '172.30.224.1'

# The type of the mocap system
# Valid options are: 'vicon', 'optitrack', 'optitrack_closed_source', 'qualisys', 'nokov', 'vrpn', 'motionanalysis'
mocap_system_type = 'vrpn'

# The name of the rigid body that represents the Crazyflie
rigid_body_name = 'cf'

# True: send position and orientation; False: send position only
send_full_pose = True

# When using full pose, the estimator can be sensitive to noise in the orientation data when yaw is close to +/- 90
# degrees. If this is a problem, increase orientation_std_dev a bit. The default value in the firmware is 4.5e-3.
orientation_std_dev = 8.0e-3

# Change the sequence according to your setup
#             x    y    z  YAW

#THESE ARE RELATIVE CHANGES
sequence = [
    (0.0, 0.0, 0.5, 0),
    (0.35, -0.3, 0, 0),
    (0.0, 0.0, -0.5, 0),
]


def take_off(cf, position):
    take_off_time = 10.0
    sleep_time = 0.1
    steps = int(take_off_time / sleep_time)
    vz = position[2] / take_off_time

    print(f'take off at {position[2]}')

    for i in range(steps):
        cf.commander.send_velocity_world_setpoint(0, 0, vz, 0)
        time.sleep(sleep_time)


def position_callback(timestamp, data, logconf):
    global drone_x, drone_y, drone_z
    drone_x = data['kalman.stateX']
    drone_y = data['kalman.stateY']
    drone_z = data['kalman.stateZ']
    vx = data['stateEstimate.vx']
    print('pos: ({}, {}, {}, {})'.format(drone_x, drone_y, drone_z, vx))


def start_position_printing(scf):
    log_conf = LogConfig(name='Position', period_in_ms=500)
    log_conf.add_variable('kalman.stateX', 'float')
    log_conf.add_variable('kalman.stateY', 'float')
    log_conf.add_variable('kalman.stateZ', 'float')
    log_conf.add_variable('stateEstimate.vx', 'float')

    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(position_callback)
    log_conf.start()

#flight via velocity setpoints
def test_flight(scf):
    cf = scf.cf

    cf.platform.send_arming_request(True)
    time.sleep(1.0)

    cf.commander.send_velocity_world_setpoint(0, 0, 0.1, 0)
    time.sleep(3)

    cf.commander.send_velocity_world_setpoint(0, 0, -0.1, 0)
    time.sleep(2)

    cf.commander.send_stop_setpoint()
    # Hand control over to the high level commander to avoid timeout and locking of the Crazyflie
    cf.commander.send_notify_setpoint_stop()

    # Make sure that the last packet leaves before the link is closed
    # since the message queue is not flushed before closing
    time.sleep(0.2)

#flight via global waypoints
def run_sequence(scf, sequence):
    cf = scf.cf

    # Arm the Crazyflie
    cf.platform.send_arming_request(True)
    time.sleep(1.0)

    #take_off(cf, sequence[0])
    #time.sleep(1.0)

    for position in sequence:
        abs_pos = (drone_x + position[0], drone_y + position[1], drone_z + position[2], 0)
        print('Setting position {}'.format(position))
        for i in range(50):
            cf.commander.send_position_setpoint(abs_pos[0],
                                                abs_pos[1],
                                                abs_pos[2],
                                                abs_pos[3])
            time.sleep(0.05)
            

    print('sequence finished')
    cf.commander.send_stop_setpoint()
    # Hand control over to the high level commander to avoid timeout and locking of the Crazyflie
    cf.commander.send_notify_setpoint_stop()

    # Make sure that the last packet leaves before the link is closed
    # since the message queue is not flushed before closing
    time.sleep(0.1)

def mc_flight(scf):
     with MotionCommander(scf, default_height=0.2) as mc:
         mc.start_up(velocity=0.1)
         time.sleep(3)
         mc.stop()
         time.sleep(2)
         mc.start_down(velocity=0.1)
         time.sleep(2)

## mocap related things

def adjust_orientation_sensitivity(cf):
    cf.param.set_value('locSrv.extQuatStdDev', orientation_std_dev)


def activate_kalman_estimator(cf):
    cf.param.set_value('stabilizer.estimator', '2')

    # Set the std deviation for the quaternion data pushed into the
    # kalman filter. The default value seems to be a bit too low.
    cf.param.set_value('locSrv.extQuatStdDev', 0.06)


def send_extpose_quat(cf, x, y, z, quat):
    """
    Send the current Crazyflie X, Y, Z position and attitude as a quaternion.
    This is going to be forwarded to the Crazyflie's position estimator.
    """
    if send_full_pose:
        cf.extpos.send_extpose(x, y, z, quat.x, quat.y, quat.z, quat.w)
    else:
        cf.extpos.send_extpos(x, y, z)

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
                if name == self.body_name:
                    if self.on_pose:
                        pos = obj.position

                        x = pos[2]
                        y = pos[0]
                        z = pos[1]

                        self.on_pose([x, y, z, obj.rotation])


if __name__ == '__main__':
    cflib.crtp.init_drivers()
    mocap_wrapper = MocapWrapper(rigid_body_name)

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

        cf = scf.cf
        trajectory_id = 1

        # Set up a callback to handle data from the mocap system
        mocap_wrapper.on_pose = lambda pose: send_extpose_quat(cf, pose[0], pose[1], pose[2], pose[3])

        adjust_orientation_sensitivity(cf)
        activate_kalman_estimator(cf)
        # activate_mellinger_controller(cf)
        #duration = upload_trajectory(cf, trajectory_id, figure8)
        reset_estimator(cf)

        # Arm the Crazyflie
        cf.platform.send_arming_request(True)
        time.sleep(1.0)

        start_position_printing(scf)
        
        #CHOOSE ONE

        run_sequence(scf, sequence)
        #test_flight(scf)
        #mc_flight(scf)