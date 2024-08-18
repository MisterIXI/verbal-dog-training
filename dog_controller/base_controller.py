import enum
import numpy as np
import threading as th
import time
import math
import Pyro5.api as api
from actions import DOG_DEFAULT_HEIGHT, FOOT_RAISE_HEIGHT, MODE_HOLD, MODE_IDLE, MODE_STAND, MODE_WALK, Action, create_action_dict
import robot_interface as go1

@api.expose
class BaseController:
    def __init__(self) -> None:
        self.action_dict = create_action_dict()
        # Dog state
        self.current_action: Action = Action.idle
        self.next_action: Action | None = Action.idle
        self.mode = MODE_STAND
        self.angle_rad = 0
        self.yawspeed = 0
        self.euler = [0, 0, 0]
        self.velocity = [0, 0]
        self.foot_raise_height = FOOT_RAISE_HEIGHT
        self.body_height = DOG_DEFAULT_HEIGHT

        self.run_loop = False
        self.loop_thread = None
        # setup udp and cmd
        self.setup_cmd()
        self.start_loop()
        
    def get_state(self) -> go1.HighState:
        self.udp.Recv()
        self.udp.GetRecv(self.state)
        return self.state
    
    def setup_cmd(self):
        # self.udp = go1.UDP(0xee, 8080, "192.168.123.161", 8082)
        self.udp = go1.UDP(0xee, 8080, "127.0.0.1", 8082)
        self.cmd = go1.HighCmd()
        self.state = go1.HighState()
        self.udp.InitCmdData(self.cmd)
    
    def set_action(self, action: Action) -> str:
        if action is not Action:
            action = Action(action)
        self.next_action = action
        print("EXT: Action was set to: " + str(action))
        return "Action set to " + str(action)
    
    def start_loop(self) -> None:
        self.run_loop = True
        self.loop_thread = th.Thread(target=self.update_loop)
        self.loop_thread.start()
    
    def stop_loop(self) -> None:
        self.run_loop = False
    
    def get_current_action(self) -> Action:
        return self.current_action
    
    def lerp_float(self, float_a, float_b, t):
        return (float_a * (1.0 - t)) + (float_b * t)
    
    def lerp_vector2(self, a_vector, b_vector, t):
        return [
            self.lerp_float(a_vector[0], b_vector[0], t),
            self.lerp_float(a_vector[1], b_vector[1], t),
        ]
    def lerp_vector3(self, a_vector, b_vector, t):
        return [
            self.lerp_float(a_vector[0], b_vector[0], t),
            self.lerp_float(a_vector[1], b_vector[2], t),
            self.lerp_float(a_vector[2], b_vector[2], t),
        ]
    def update_loop(self):
        LOOP_DELAY = 0.001
        # for start, load the current action and start it from 0
        last_step = None
        curr_list = self.action_dict[self.current_action].copy()
        curr_step = curr_list.pop(0)
        start_time = time.time()
        curr_time = 0
        last_time = 0
        while self.run_loop:
            # calculate t for interpolation
            if curr_step[0] - last_time <= 0:
                t = 1
            else:
                t = (curr_time - last_time) / (curr_step[0] - last_time)
                # clamp t to 0-1
                t = max(0, min(1, t))
            # print(f"t: {t}")
            # check for mode and set all values correctly
            self.mode = curr_step[1]
            self.gaitType = 0
            # reset all values to default
            self.euler = [0, 0, 0]
            self.yawspeed = 0
            self.velocity = [0, 0]
            self.foot_raise_height = FOOT_RAISE_HEIGHT
            self.body_height = DOG_DEFAULT_HEIGHT
            
            if self.mode == MODE_IDLE:
                pass
            elif self.mode == MODE_STAND:
                if last_step is None or (last_step is not None and not(last_step[1] == MODE_STAND or last_step[1] == MODE_WALK)):
                    self.body_height = curr_step[2]
                    self.euler = curr_step[3]
                elif last_step[1] == MODE_STAND:
                    self.body_height = self.lerp_float(last_step[2], curr_step[2], t)
                    self.euler = self.lerp_vector3(last_step[3], curr_step[3], t)
                else:
                    self.body_height = curr_step[2]
                    self.euler = curr_step[3]
            elif self.mode == MODE_WALK:
                self.gaitType = 1
                # don't interpolate foot raise height, just set it to target
                self.foot_raise_height = curr_step[5]
                if last_step is None or last_step[1] != MODE_WALK:
                    self.body_height = curr_step[2]
                    # self.angle_rad = curr_step[3]
                    self.yawspeed = curr_step[3]
                    self.velocity = curr_step[4]
                else:
                    self.body_height = self.lerp_vector2(last_step[2], curr_step[2], t)
                    # difference in angle
                    # angle_diff = math.radians(curr_step[3] - last_step[3])
                    # calculate raidans per second turnspeed
                    # self.yawspeed = angle_diff / (curr_step[0] - last_step[0])
                    self.yawspeed = curr_step[3]
                    self.velocity = curr_step[4]
                print(f"yawspeed: {self.yawspeed}")
            self.cmd.gaitType = self.gaitType
            # set cmd values and send
            self.cmd.mode = self.mode
            self.cmd.euler = self.euler
            # print(f"current euler: {self.euler}")
            self.cmd.yawSpeed = self.yawspeed
            self.cmd.velocity = self.velocity
            self.cmd.footRaiseHeight = self.foot_raise_height
            self.cmd.bodyHeight = self.body_height
            # print(f"body_height: {self.body_height}")
            self.udp.SetSend(self.cmd)
            if self.current_action != Action.idle:
                self.udp.Send()
            # receive state
            self.get_state()
            # check if current step is done and move to the next one
            curr_time = time.time() - start_time
            if self.next_action != None:
                self.current_action = self.next_action
                self.next_action = None
                print("Starting action: " + str(self.current_action))
                curr_list = self.action_dict[self.current_action].copy()
                # check for hold in new action
                curr_step = curr_list.pop(0)
                last_step = None
                start_time = time.time()
                curr_time = 0
                last_time = 0
            elif curr_time >= curr_step[0]:
                if len(curr_list) > 0:
                    last_time = curr_step[0]
                    last_step = curr_step
                    curr_step = curr_list.pop(0)
                else:
                    # finished with current action
                    if self.current_action == Action.idle:
                        pass
                    elif self.current_action == Action.return_to_idle:
                        self.current_action = Action.idle
                        print("Back to idle")
                        curr_list = self.action_dict[self.current_action].copy()
                        curr_step = curr_list.pop(0)
                        last_step = None
                        start_time = time.time()
                        curr_time = 0
                        last_time = 0
                    else:
                        self.current_action = Action.idle
                        print("Returning to idle")
                        curr_list = self.action_dict[self.current_action].copy()
                        curr_step = curr_list.pop(0)
                        last_step = None
                        start_time = time.time()
                        curr_time = 0
                        last_time = 0
            # else:
            #     print(f"time left: {curr_time}; {curr_step[0]}")
            # delay update very slightly
            time.sleep(LOOP_DELAY)
            