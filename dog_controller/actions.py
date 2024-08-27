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
    hinlegen = 3
    schütteln = 4
    spielen = 5
    drehen = 6
    springen = 7
    buddeln = 8
    # jump_lr = 5


FOOT_RAISE_HEIGHT = 0.08
DOG_DEFAULT_HEIGHT = 0.024
DOG_LOWEST_HEIGHT = 0.010
MODE_HOLD = -1
MODE_IDLE = 0
MODE_STAND = 1
MODE_WALK = 2
MODE_CONT_WALK = 3
MODE_FORCE_DOWN = 5
MODE_FORCE_UP = 6
MODE_DANCE1 = 12
MODE_DANCE2 = 13

FULL_ROT_RAD = 6.283185 # multiply by offset to achieve full rotation


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
            # (0, MODE_WALK, DOG_DEFAULT_HEIGHT, 0, [0.001, 0], FOOT_RAISE_HEIGHT),
            # (3, MODE_WALK, DOG_DEFAULT_HEIGHT, 0, [0.1, 0], FOOT_RAISE_HEIGHT),
            (0, MODE_CONT_WALK, DOG_DEFAULT_HEIGHT, 0, [0, 0], FOOT_RAISE_HEIGHT),
            (1.5, MODE_CONT_WALK, DOG_DEFAULT_HEIGHT, 0, [0, 0], FOOT_RAISE_HEIGHT),
            (3, MODE_STAND, DOG_DEFAULT_HEIGHT, [0, 0, 0]),
            (6, MODE_STAND, DOG_DEFAULT_HEIGHT, [0, 0, 0]),
            # (0, MODE_IDLE, DOG_DEFAULT_HEIGHT, [0, 0, 0]),
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
            (2, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0.0, 0]),
        ]),
        Action.hinlegen: ([
            (0, MODE_STAND, DOG_DEFAULT_HEIGHT, [0, 0, 0]),
            (1, MODE_FORCE_UP),
            (2, MODE_FORCE_DOWN),
            (4, MODE_FORCE_DOWN),
            (5, MODE_FORCE_UP),
            (5.5, MODE_STAND, DOG_DEFAULT_HEIGHT, [0, 0, 0]),
        ]),
        Action.schütteln: ([
            (0, MODE_FORCE_UP, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            (0.25, MODE_STAND, DOG_DEFAULT_HEIGHT,   [0, 0, 0]),
            (0.75, MODE_STAND, DOG_DEFAULT_HEIGHT,   [1.5, 0, 0]),
            (1.25, MODE_STAND, DOG_DEFAULT_HEIGHT,     [-1.5, 0, 0]),
            (1.75, MODE_STAND, DOG_DEFAULT_HEIGHT,     [1.5, 0, 0]),
            (2.25, MODE_STAND, DOG_DEFAULT_HEIGHT,     [-1.5, 0, 0]),
            (2.75, MODE_STAND, DOG_DEFAULT_HEIGHT,     [1.5, 0, 0]),
            (3, MODE_STAND, DOG_DEFAULT_HEIGHT,   [0, 0, 0]),
            (3.5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
        ]),
        Action.spielen: ([
            (0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            (0.75, MODE_STAND, DOG_DEFAULT_HEIGHT,  [0, 1, 0]),
            (1.25, MODE_STAND, DOG_DEFAULT_HEIGHT,  [0, 1, 0]),
            (1.5, MODE_STAND, DOG_DEFAULT_HEIGHT,   [0, 1, 0.65]),
            (2, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 1, -0.65]),
            (2.5, MODE_STAND, DOG_DEFAULT_HEIGHT,   [0, 1, 0.65]),
            (3, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 1, -0.65]),
            (3.5, MODE_STAND, DOG_DEFAULT_HEIGHT,   [0, 1, 0.65]),
            (4, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 1, -0.65]),
            (4.5, MODE_STAND, DOG_DEFAULT_HEIGHT,   [0, 1, 0.65]),
            (5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 1, -0.65]),
            (5.25, MODE_STAND, DOG_DEFAULT_HEIGHT,  [0, 1, 0]),
            (6, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            (7, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            # (8.2, MODE_WALK, DOG_DEFAULT_HEIGHT, 0, [0.1, 0], FOOT_RAISE_HEIGHT),
            # (8.4, MODE_WALK, DOG_DEFAULT_HEIGHT, 0, [-0.1, 0], FOOT_RAISE_HEIGHT),
            (8.5, MODE_CONT_WALK, DOG_DEFAULT_HEIGHT, 0, [0,0], FOOT_RAISE_HEIGHT),
            (10, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
        ]),
        Action.drehen: ([
            (0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            (6.8, MODE_WALK, DOG_DEFAULT_HEIGHT, FULL_ROT_RAD/5.0, [0, 0], FOOT_RAISE_HEIGHT),
            (8.5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            (10, MODE_CONT_WALK, DOG_DEFAULT_HEIGHT, 0, [0,0], FOOT_RAISE_HEIGHT),
            (11.5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
        ]),
        Action.springen: ([
            (0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            (3.5, MODE_DANCE1),
            (4, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            (5.5, MODE_CONT_WALK, DOG_DEFAULT_HEIGHT, 0, [0,0], FOOT_RAISE_HEIGHT),
            (7, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
        ]),
        Action.buddeln: ([
            (0, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            (4, MODE_DANCE2),
            (4.5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
            (6, MODE_CONT_WALK, DOG_DEFAULT_HEIGHT, 0, [0,0], FOOT_RAISE_HEIGHT),
            (7.5, MODE_STAND, DOG_DEFAULT_HEIGHT,     [0, 0, 0]),
        ]),
    }
