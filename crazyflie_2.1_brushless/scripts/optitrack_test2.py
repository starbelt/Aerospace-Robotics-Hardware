# -*- coding: utf-8 -*-
"""
Crazyflie 2.1 Brushless + OptiTrack/Motive (VRPN) external pose with watchdog + reconnect.
- Starts position-only (SEND_FULL_POSE=False). Set True after stable hover.
- Auto-lands if mocap frames stop for > MOCAP_TIMEOUT_S.
- VRPN client auto-reconnects on drop.
"""

import time
from threading import Thread, Event

import motioncapture

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.mem import MemoryElement
from cflib.crazyflie.mem import Poly4D
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.utils.reset_estimator import reset_estimator

# ===== USER SETTINGS =====
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

HOST_NAME = '172.30.224.1'          # Motive/VRPN IP
MOCAP_TYPE = 'vrpn'                  # 'vrpn' for Motive VRPN
RIGID_BODY_NAMES = ('cf', 'RigidBody 1')  # try these names in order

SEND_FULL_POSE = False               # start pos-only; set True after stable hover
EXT_QUAT_STD_DEV = 0.04              # radians; ~0.03–0.06 for debugging
WARMUP_FRAMES = 60                   # ~0.5 s at 120 Hz
MOCAP_TIMEOUT_S = 0.3                # auto-land if no mocap for this long

# ===== Example short figure-8 trajectory =====
figure8 = [
    [0.400000,-0.000466,0.000000,0.000000,1.069075,-0.032915,-0.370393,-0.377175,-0.283698,-0.000466,0.000000,0.000000,1.069075,-0.032915,-0.370393,-0.377175,-0.283698,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
    [0.400000,0.061309,0.426012,0.808398,-0.313195,-0.343948,-0.052895,0.102677,0.146154,0.061309,0.426012,0.808398,-0.313195,-0.343948,-0.052895,0.102677,0.146154,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
    [0.400000,0.332326,0.838074,0.139378,-0.685763,0.082302,0.189539,0.091251,-0.074926,0.332326,0.838074,0.139378,-0.685763,0.082302,0.189539,0.091251,-0.074926,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
    [0.400000,0.650267,0.669199,-0.464294,-0.201150,0.132539,0.082640,0.037794,0.012290,0.650267,0.669199,-0.464294,-0.201150,0.132539,0.082640,0.037794,0.012290,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
    [0.400000,0.835200,0.248395,-0.508390,0.202525,0.154643,0.120197,0.078274,0.046132,0.835200,0.248395,-0.508390,0.202525,0.154643,0.120197,0.078274,0.046132,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
]


# ===== Mocap thread with auto-reconnect & last-seen timestamp =====
class MocapWrapper(Thread):
    def __init__(self, names):
        Thread.__init__(self, daemon=True)
        self.names = set(names)
        self.on_pose = None
        self._stay_open = True
        self.last_ts = 0.0
        self._stop_evt = Event()
        self.start()

    def close(self):
        self._stay_open = False
        self._stop_evt.set()

    def _connect(self):
        while self._stay_open:
            try:
                print("Connecting to mocap…")
                mc = motioncapture.connect(MOCAP_TYPE, {'hostname': HOST_NAME})
                print("Mocap connected.")
                return mc
            except Exception as e:
                print(f"Failed to connect to mocap: {e}. Retrying in 1s…")
                self._stop_evt.wait(1.0)
        return None

    def run(self):
        mc = self._connect()
        if mc is None:
            return
        while self._stay_open:
            try:
                mc.waitForNextFrame()
                tnow = time.monotonic()
                # Use whichever rigid body name is present
                for name, obj in mc.rigidBodies.items():
                    if (name in self.names) and self.on_pose:
                        pos = obj.position  # meters (Scale=1)
                        self.on_pose([pos[0], pos[1], pos[2], obj.rotation])
                        self.last_ts = tnow
                        break
            except Exception as e:
                print(f"Mocap connection dropped: {e}. Reconnecting…")
                # Attempt reconnect
                try:
                    mc.close()
                except Exception:
                    pass
                mc = self._connect()
                if mc is None:
                    return


# ===== Helpers =====
def send_extpose_quat(cf, x, y, z, quat):
    if SEND_FULL_POSE:
        cf.extpos.send_extpose(x, y, z, quat.x, quat.y, quat.z, quat.w)
    else:
        cf.extpos.send_extpos(x, y, z)

def _safe_set(cf, name, value):
    try:
        cf.param.set_value(name, str(value))
        print(f"Set {name} = {value}")
    except KeyError:
        print(f"Param {name} not found; skipping")

def configure_runtime_params(cf):
    _safe_set(cf, 'stabilizer.estimator',  '2')  # EKF2
    _safe_set(cf, 'stabilizer.controller', '2')  # Mellinger
    _safe_set(cf, 'commander.enHighLevel', '1')  # HL
    _safe_set(cf, 'locSrv.extQuatStdDev',  EXT_QUAT_STD_DEV)
    _safe_set(cf, 'locSrv.useExtPose',     '1')  # some builds don't have this; ok to skip

def upload_trajectory(cf, trajectory_id, trajectory):
    trajectory_mem = cf.mem.get_mems(MemoryElement.TYPE_TRAJ)[0]
    trajectory_mem.trajectory = []
    total_duration = 0.0
    for row in trajectory:
        duration = row[0]
        x = Poly4D.Poly(row[1:9]); y = Poly4D.Poly(row[9:17])
        z = Poly4D.Poly(row[17:25]); yaw = Poly4D.Poly(row[25:33])
        trajectory_mem.trajectory.append(Poly4D(duration, x, y, z, yaw))
        total_duration += duration
    trajectory_mem.write_data_sync()
    cf.high_level_commander.define_trajectory(trajectory_id, 0, len(trajectory_mem.trajectory))
    return total_duration

def run_sequence_with_watchdog(cf, trajectory_id, duration, mocap: MocapWrapper):
    hl = cf.high_level_commander
    print("Taking off…")
    hl.takeoff(0.5, 2.0)
    start = time.monotonic()
    # climb + settle
    while time.monotonic() - start < 3.0:
        if time.monotonic() - mocap.last_ts > MOCAP_TIMEOUT_S:
            print("Mocap timeout during takeoff → landing")
            hl.land(0.0, 1.5); time.sleep(1.6); hl.stop()
            return False
        time.sleep(0.01)

    print("Starting trajectory…")
    hl.start_trajectory(trajectory_id, 1.0, True)  # relative=True

    t0 = time.monotonic()
    while time.monotonic() - t0 < duration:
        if time.monotonic() - mocap.last_ts > MOCAP_TIMEOUT_S:
            print("Mocap timeout during trajectory → landing")
            hl.land(0.0, 1.5); time.sleep(1.6); hl.stop()
            return False
        time.sleep(0.01)

    print("Landing…")
    hl.land(0.0, 2.0)
    # monitor mocap during landing too
    start = time.monotonic()
    while time.monotonic() - start < 2.0:
        if time.monotonic() - mocap.last_ts > MOCAP_TIMEOUT_S:
            print("Mocap timeout during landing – continuing to stop")
            break
        time.sleep(0.01)
    hl.stop()
    return True


# ===== Main =====
if __name__ == '__main__':
    cflib.crtp.init_drivers()

    mocap_wrapper = MocapWrapper(RIGID_BODY_NAMES)

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        cf = scf.cf
        trajectory_id = 1

        # --- stream mocap + warm-up counter ---
        global good_frames
        good_frames = 0

        def _on_pose(pose):
            global good_frames
            x, y, z, q = pose
            # NaN-safe check
            if all(v == v for v in [x, y, z]):
                good_frames = min(good_frames + 1, WARMUP_FRAMES)
            else:
                good_frames = 0
            send_extpose_quat(cf, x, y, z, q)

        mocap_wrapper.on_pose = _on_pose

        # Configure flight stack
        configure_runtime_params(cf)

        # Wait for stable mocap before EKF reset
        print("Waiting for stable mocap frames…")
        t_wait0 = time.monotonic()
        while good_frames < WARMUP_FRAMES:
            time.sleep(0.01)
        print("Mocap stable. Resetting estimator…")
        reset_estimator(cf)

        # Arm after reset (keep streaming ext pose)
        cf.platform.send_arming_request(True)
        time.sleep(1.0)

        # Upload trajectory and fly with watchdog
        duration = upload_trajectory(cf, trajectory_id, figure8)
        print(f'The sequence is {duration:.1f} s long')
        ok = run_sequence_with_watchdog(cf, trajectory_id, duration, mocap_wrapper)

        # Disarm for safety
        cf.platform.send_arming_request(False)
        time.sleep(0.2)

    mocap_wrapper.close()
