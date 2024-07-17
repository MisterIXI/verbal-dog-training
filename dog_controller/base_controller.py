import robot_interface as go1
import enum
import numpy as np
import threading as th
import time
import math
import Pyro5.api as api
from actions import DOG_DEFAULT_HEIGHT, FOOT_RAISE_HEIGHT, MODE_IDLE, MODE_STAND, MODE_WALK, Action, create_action_dict

@api.expose
class BaseController:
    def __init__(self) -> None:
        self.action_dict = create_action_dict()
        # Dog state
        self.current_action: Action = Action.idle
        self.next_action: Action = Action.idle
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
        
    def get_state(self) -> go1.HighState:
        self.udp.Recv()
        self.udp.GetRecv(self.state)
        return self.state
    
    def setup_cmd(self):
        self.udp = go1.UDP(0xee, 8080, "192.168.123.161", 8082)
        self.cmd = go1.HighCmd()
        self.state = go1.HighState()
        self.udp.InitCmdData(self.cmd)
    
    def set_action(self, action: Action) -> str:
        if self.current_action != Action.idle:
            print("Cannot set action while current action is not idle")
            return "Cannot set action while current action is not idle"
        self.next_action = action
        return "Action set to " + str(action)
    
    def start_loop(self) -> None:
        self.run_loop = True
        self.loop_thread = th.Thread(target=self.update_loop)
        self.loop_thread.start()
    
    def stop_loop(self) -> None:
        self.run_loop = False
    
    def get_current_action(self) -> Action:
        return self.current_action
    
    def update_loop(self):
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
            # check for mode and set all values correctly
            self.mode = curr_step[1]
            # reset all values to default
            self.euler = [0, 0, 0]
            self.yawspeed = 0
            self.velocity = [0, 0]
            self.foot_raise_height = FOOT_RAISE_HEIGHT
            self.body_height = DOG_DEFAULT_HEIGHT
            
            if self.mode == MODE_IDLE:
                pass
            elif self.mode == MODE_STAND:
                if last_step is None:
                    self.body_height = curr_step[2]
                    self.euler = curr_step[3]
                else:
                    self.body_height = np.interp(t, last_step[2], curr_step[2])
                    self.euler = [np.interp(t, last_step[3], curr_step[3])]
            elif self.mode == MODE_WALK:
                # don't interpolate foot raise height, just set it to target
                self.foot_raise_height = curr_step[5]
                if last_step is None:
                    self.body_height = curr_step[2]
                    self.angle_rad = curr_step[3]
                    self.velocity = curr_step[4]
                else:
                    self.body_height = np.interp(t, last_step[2], curr_step[2])
                    # difference in angle
                    angle_diff = math.radians(curr_step[3] - last_step[3])
                    # calculate raidans per second turnspeed
                    self.yawspeed = angle_diff / (curr_step[0] - last_step[0])
                    self.velocity = [
                        np.interp(t, last_step[4][0], curr_step[4][0]),
                        np.interp(t, last_step[4][1], curr_step[4][1])
                    ]
            # set cmd values and send
            self.cmd.mode = self.mode
            self.cmd.euler = self.euler
            self.cmd.yawSpeed = self.yawspeed
            self.cmd.velocity = self.velocity
            self.cmd.footRaiseHeight = self.foot_raise_height
            self.cmd.bodyHeight = self.body_height
            self.udp.SetSend(self.cmd)
            self.udp.Send()
            # receive state
            self.get_state()
            # check if current step is done and move to the next one
            curr_time = time.time() - start_time
            if curr_time >= curr_step[0]:
                if len(curr_list) == 0:
                    # finished with current action
                    if self.current_action == Action.idle:
                        # if idle, loop until next action is set
                        if self.next_action != Action.idle:
                            self.current_action = self.next_action
                            self.next_action = Action.idle
                            curr_list = self.action_dict[self.current_action].copy()
                            start_time = time.time()
                            curr_time = 0
                            last_time = 0
                    elif self.current_action == Action.return_to_idle:
                        self.current_action = Action.idle
                        curr_list = self.action_dict[self.current_action].copy()
                        start_time = time.time()
                        curr_time = 0
                        last_time = 0
                    else:
                        # finished neither idle and return animation
                        self.current_action = Action.return_to_idle
                        curr_list = self.action_dict[self.current_action].copy()
                        start_time = time.time()
                        curr_time = 0
                        last_time = 0
            # delay update very slightly
            time.sleep(0.01)
            