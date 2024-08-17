from ast import List, Tuple
import typing as tp
import enum


class Action(enum.Enum):
    # Actions for the robot
    # base actions
    return_to_idle = -1
    idle = 0
    attention = 1
    attention_cancel = 2
    lie_down = 3
    shake = 4
    vibe_8 = 5
    turn_360 = 6
    # jump_lr = 5


FOOT_RAISE_HEIGHT = 0.08
DOG_DEFAULT_HEIGHT = 0.024
DOG_LOWEST_HEIGHT = 0.010
MODE_HOLD = -1
MODE_IDLE = 0
MODE_STAND = 1
MODE_WALK = 2
MODE_FORCE_DOWN = 5
MODE_FORCE_UP = 6


def create_action_dict() -> tp.Dict[Action, tp.List[tp.Tuple]]:
    return {
        # EULER (in rad): [roll, pitch, yaw]
        # format: Action: (hold_until, move_arr)
        # https://unitree-docs.readthedocs.io/en/latest/get_started/Go1_Edu.html#go1-sdk-highcmd-mode
        # move arr depends on the mode:
        # move_arr: mode 0 IDLE:        [time, mode]
        # move_arr: mode 1 STAND:       [time, mode, height, euler]
        # move_arr: mode 2 WALK:        [time, mode, height, desired_angle, velocity_vector, foot_raise_height]
        # move_arr: mode 5 FORCE_DOWN:  [time, mode]
        # move_arr: mode 6 FORCE_UP:    [time, mode]
        Action.return_to_idle: ([
            # (0, MODE_WALK, DOG_DEFAULT_HEIGHT, 0, [0, 0], FOOT_RAISE_HEIGHT),
            # (3, MODE_WALK, DOG_DEFAULT_HEIGHT, 0, [0, 0], FOOT_RAISE_HEIGHT),
            # (3, MODE_STAND, DOG_DEFAULT_HEIGHT, [0, 0, 0]),
            # (4, MODE_STAND, DOG_DEFAULT_HEIGHT, [0, 0, 0]),
            (0, MODE_IDLE, DOG_DEFAULT_HEIGHT, [0, 0, 0]),
        ]),
        Action.idle: ([
            (0, MODE_IDLE, DOG_DEFAULT_HEIGHT, [0, 0, 0]),
        ]),
        Action.attention: ([
            (0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, -0.0, 0]),
            (1, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, -0.65, 0]),
            (120, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, -0.65, 0]),
        ]),
        Action.attention_cancel: ([
            (0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, -0.65, 0]),
            (1.5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0.0, 0]),
        ]),
        Action.lie_down: ([
            (0, MODE_STAND, DOG_DEFAULT_HEIGHT, [0, 0, 0]),
            (1, MODE_FORCE_UP),
            (2, MODE_FORCE_DOWN),
            (4, MODE_FORCE_DOWN),
            (5, MODE_FORCE_UP),
            (5.5, MODE_STAND, DOG_DEFAULT_HEIGHT, [0, 0, 0]),
        ]),
        Action.shake: ([
            (0, MODE_FORCE_UP, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            (0.5, MODE_STAND, DOG_DEFAULT_HEIGHT,   [0, 0, 0]),
            (1.0, MODE_STAND, DOG_DEFAULT_HEIGHT,   [0.9, 0, 0]),
            (1.01, MODE_STAND, DOG_DEFAULT_HEIGHT,     [-0.9, 0, 0]),
            (3.9, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0.9, 0, 0]),
            (4, MODE_STAND, DOG_DEFAULT_HEIGHT,     [-0.9, 0, 0]),
            (5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0.6, 0, 0]),
            (5.5, MODE_STAND, DOG_DEFAULT_HEIGHT,   [0, 0, 0]),
            (6.5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
        ]),
        Action.vibe_8: ([
            (0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            (1.0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0.5, -0.5, 0]),
            (1.5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0.9, 0, 0]),
            (2.0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0.5, 0.5, 0]),
            (2.5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            (3.0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [-0.5, -0.5, 0]),
            (3.5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [-0.9, 0, 0]),
            (4.0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0.5, 0.5, 0]),
            (4.5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            (5.0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0.5, -0.5, 0]),
            (5.5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0.9, 0, 0]),
            (6.0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0.5, 0.5, 0]),
            (6.5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            (7.0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [-0.5, -0.5, 0]),
            (7.5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [-0.9, 0, 0]),
            (8.0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0.5, 0.5, 0]),
            (8.5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
        ]),
        Action.turn_360: ([
            (0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            (0.5, MODE_WALK, DOG_DEFAULT_HEIGHT, 0, [1, 0.5], FOOT_RAISE_HEIGHT),
            (3, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
        ]),
    }
