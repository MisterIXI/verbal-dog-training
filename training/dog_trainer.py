from argparse import Action
from time import sleep

import regex as re
from numpy import add
from sympy import true
import custom_speech_recognition.speech_recognition as sr
import custom_llm.llm_api as llm_api
import dog_controller.pyro_connector as dc
import dog_controller.actions as actions
import dog_controller.custom_led_lib as led
import enum
import threading as th
import Levenshtein as lev
from collections import defaultdict
import random

class t_state(enum.Enum):
    idle = 0
    listening = 1
    thinking = 2
    acting = 3


class dog_trainer:
    LEVENSHTEIN_THRESHOLD = 5
    # COMMANDS = [str(action)[7:] for action in actions.Action if action.value > 0]
    COMMANDS = [str(action)[7:] for action in [
        actions.Action.hinlegen,
        actions.Action.schütteln,
        actions.Action.spielen,
        actions.Action.drehen,
        actions.Action.springen,
        actions.Action.tanzen,
    ]]
    def __init__(self, print_callback: callable, sr_model: str, state_callback: callable, dog_controller: str) -> None:
        print("Commands: ", self.COMMANDS)
        self.state_callback = state_callback
        self.state = t_state.idle
        self.sr = None
        self.llm = None
        self.dc = None
        self.learned_commands = {}
        self.learned_negatives:defaultdict[str,list] = defaultdict(list)
        self._print_cb = print_callback
        self.loaded = {"SR": False, "LLM": False, "DC": False}
        self.sr_model = sr_model
        self.dog_controller = dog_controller
        self.train_step_event = th.Event()
        self.wait_for_feedback = th.Event()
        self.feedback: bool = False
        self.is_running = True
        self.threads = {}
        self.auto_feedback = False
        self.trainer_state_cb = None
        self.led = led.LedController()
        self.led.clear_led_all()
        self.total_positives = 0
        self.total_negatives = 0

    def _print(self, text, source="DT", color="white"):
        self._print_cb(text,source, color)

    def _load_sr(self):
        if self.loaded["SR"]:
            return
        model = sr.Model(self.sr_model)
        self.sr: sr.recognizer = sr.recognizer(model, self._print_cb, "german")
        self.threads["SR"] = th.Thread(target=self.sr.run).start()
        self._print("Finished loading speech recognition.", color="lightgreen")
        self.loaded["SR"] = True

    def _load_llm(self):
        if self.loaded["LLM"]:
            return
        self.llm = llm_api.LLM_API(self._print_cb, commands=self.COMMANDS ,obfuscate_names=False)
        if not self.llm.test_if_running():
            self._print("Language model query could not be sent. Is the server running?", color="red")
            return
        self.threads["LLM"] = th.Thread(target=self.llm.prompt).start()
        self._print("Finished loading language model.", color="lightgreen")
        self.loaded["LLM"] = True

    def _load_dc(self):
        if self.loaded["DC"]:
            return
        if self.dog_controller == "Pyro_dog":
            address = "192.168.123.161"
        elif self.dog_controller == "Dummy":
            address = "localhost"
        elif self.dog_controller == "Pyro_wsl":
            address = "172.21.201.135"
        else:
            self._print("Invalid dog controller specified", "DT", "red")
            return
        if self.dc is None:
            self.dc = dc.remote_controller(self._print_cb, self.state_callback, host_adress=address)
        if not self.dc.is_connected:
            self.dc.host_adress = address
            self.dc.start_pyro_loop()
        self.dc.has_finished_connection_attempt.wait()
        if not self.dc.is_connected:
            self._print("Could not connect to remote controller", "DT", "red")
            return
        self._print("Finished loading dog controller.", color="lightgreen")
        self.loaded["DC"] = True

    def load_all(self):
        self._print("Loading all...")
        self._print("Loading speech recognition...")
        self._print("(This might download the specific model if loading for the first time and take a while.)")
        self._load_sr()
        self._print("Loading language model...")
        self._load_llm()
        self._print("Loading dog controller...")
        self._load_dc()

    def is_all_loaded(self):
        return all(self.loaded.values())

    def reset_data(self):
        self.learned_commands = {}

    def wait_for_hotword(self):
        assert self.is_all_loaded(), "Not all components are loaded."
        self._print("Waiting for hotword...", color="yellow")
        self.trainer_state_update("Waiting for hotword...", "yellow")
        # loop until hotword is detected
        # TODO: Light up cheecks to signal ready for hotword 
        while True:
            self._print("Waiting for SR...")
            self.led.breathe_single_color(self.led.BLUE)
            self.sr.thread_event.set()
            self.sr.finished_listening.wait()
            self.sr.finished_listening.clear()
            self.led.breathe_single_color(self.led.YELLOW)
            self.sr.data_ready.wait()
            self.sr.data_ready.clear()
            self._print("Detected words: " + self.sr.data)
            check = self.sr.data.lower()
            if "techie" in check or "take it" in check or "hey" in check:
                self._print("Hotword detected.", color="lightgreen")
                break

    def train_step(self, feedback_unlock_cb: callable = None):
        assert self.is_all_loaded(), "Not all components are loaded."
        # Voice recognition
        # start listening and wait for data
        self.trainer_state_update("Listening for command...", "yellow")
        self._print("Triggering voice recognition...")
        self.dc.set_action(actions.Action.attention)
        self.led.breathe_single_color(self.led.BLUE)
        self.sr.thread_event.set()
        self.sr.finished_listening.wait()
        self.sr.finished_listening.clear()
        self.dc.set_action(actions.Action.attention_cancel)
        self.led.breathe_single_color(self.led.YELLOW)
        self.sr.data_ready.wait()
        self.sr.data_ready.clear()
        if not self.sr.is_running:
            print("Cancelled training step.")
            self.trainer_state_update("Idle", "lightgreen")
            self.led.clear_led_all()
            return
        data = self.sr.data
        #### Command preprocessing
        # set all to lower case
        data = data.lower()
        # filter out all characters besides alphanumeric, whitespace and umlauts with regex
        data = re.sub(r'[^\w äöüß]', '', data)
        if data is None or data == "":
            self._print("No voice input received. Cancelling training step...")
            self.led.start_breathing_color(0.25, self.led.RED, self.led.OFF)
            sleep(3)
            self.trainer_state_update("Idle", "lightgreen")
            self.led.clear_led_all()
            sleep(2)
            return
        self._print("Voice recognition finished.")
        self._print("Recognized: " + data,color="lightgreen")
        self.trainer_state_update("Checking command...", "yellow")
        #### Check if exact match in learned commands
        # check if command is in confirmed dict
        self._print("Checking if command is in confirmed dict...")
        command = None
        if data in self.learned_commands:
            command = self.learned_commands[data]
            self._print("Found command in confirmed dict: " + command)
        #### Check if any commands in learned commands is < LEVENSHTEIN_THRESHOLD --> find closest of them
        # if prev didn't work: levenshtein distance to find closest confirmed command
        if command is None:
            self._print("Command not found in confirmed dict.")
            self._print("Calculating Levenshtein distance...")
            result = self.find_closest(data, self.learned_commands.keys())
            if result is not None:
                command = self.learned_commands[result]
                self._print(f"Found closest command: {command} with distance {lev.distance(data, command)}", color="lightgreen")
            else:
                self._print(f"No command found with distance < {self.LEVENSHTEIN_THRESHOLD}.", color="yellow")
        #### Check if any commands in learned negatives is < LEVENSHTEIN_THRESHOLD --> roll from remaining commands of the one found
        # if prev didn't work: check for negative associations and roll a remaining command
        # if already associated, the llm should have selected it last time and would select it again most likely
        if command is None:
            self._print("Checking for negative associations...")
            result = self.find_closest(data, self.learned_negatives.keys())
            if result is not None:
                available_commands = [com for com in self.COMMANDS if com not in self.learned_negatives[result]]
                if len(available_commands) > 0:
                    command = random.choice(available_commands)
                    self._print(f"Found a close prompt with negative association: {data} -> {command}. Rolling from the remaining pool: {available_commands}.", color="yellow")
                    self._print(f"Rolled command: {command}", color="lightgreen")
                else:
                    command = random.choice(self.COMMANDS)
                    self._print(f"Found a close prompt with negative association: {data} -> {command}. But all commands have a negative association, rolling randomly...", color="yellow")
                    self._print(f"Rolled command: {command}", color="lightgreen")
        #### Query LLM for command
        # if prev didn't work: ask llm for command
        if command is None:
            self._print("Asking language model for command...")
            self.trainer_state_update("Querying LLM...", "yellow")
            command = self.llm.trigger_prompt(data)
            self.llm.data_ready.wait()
            self.llm.data_ready.clear()
            command = self.llm.data
            if command is None:
                # when llm errored out
                self._print("Language model errored out. Cancelling training step...")
                self.led.start_breathing_color(0.25, self.led.RED, self.led.OFF)
                sleep(3)
                self.trainer_state_update("Idle", "lightgreen")
                self.led.clear_led_all()
                sleep(2)
                return
            self._print("Language model returned: " + command)
        #### Check if exact match in negative commands --> reroll from remaining commands if the case
        # when the current command has a negative association with the prompt
        if command in self.learned_negatives[data]:
            old_command = command
            self._print("Command is in negative list. Rerolling...", color="red")
            available_commands = [com for com in self.COMMANDS if com not in self.learned_negatives[data]]
            # if no commands are available, roll randomly
            if len(available_commands) == 0:
                self._print("No non-negative commands available. Rolling completely at random...", color="red")
                command = random.choice(self.COMMANDS)
            else:
                self._print(f"Selecting from the remaining commands: {available_commands}")
                command = random.choice(available_commands)
            self._print(f"Command reroll: {old_command} -> {command}", color="lightgreen")
        #### If error in command selection, cancel training step
        if command not in self.COMMANDS or command is None:
            self._print("Command not recognized. Cancelling training step...", color="red")
            self.led.clear_led_all()
            self.trainer_state_update("Idle", "lightgreen")
            return
        action = actions.Action[command]
        self.led.breathe_single_color(self.led.GREEN)
        # execute command
        self._print(f"Executing command: {command}...", color="yellow")
        self.trainer_state_update("Executing command...", "yellow")
        if not self.dc.is_connected:
            self._print("Not connected to remote controller", "DC", "red")
            self.trainer_state_update("Idle", "lightgreen")
            return
        self.dc.set_action(action)
        self._print(f"Waiting for idle from dog controller...")
        self.dc.wait_for_idle.clear()
        self.dc.wait_for_idle.wait()
        self.dc.wait_for_idle.clear()
        self.dc.set_action(actions.Action.attention)
        # get feedback from user
        self._print("Waiting for feedback from user", color="yellow")
        if self.auto_feedback:
            # auto feedback with speech recognition
            self.trainer_state_update("Listening for feedback...", "yellow")
            while True:
                # record once
                self.led.breathe_single_color(self.led.BLUE)
                self.sr.thread_event.set()
                self.sr.finished_listening.wait()
                self.sr.finished_listening.clear()
                self.led.breathe_single_color(self.led.YELLOW)
                self.sr.data_ready.wait()
                self.sr.data_ready.clear()
                self._print("Feedback recognized: " + self.sr.data)
                # check for positive feedback
                if "ja" in self.sr.data.lower() or "gut" in self.sr.data.lower():
                    self.feedback = True
                    self._print("Positive feedback recognized.", color="yellow")
                    break
                # check for negative feedback
                if "nein" in self.sr.data.lower() or "falsch" in self.sr.data.lower():
                    self.feedback = False
                    self._print("Negative feedback recognized.", color="yellow")
                    break
        else:
            # feedback with buttons
            self.led.breathe_single_color(self.led.YELLOW)
            self.trainer_state_update("Waiting for feedback BTN...", "yellow")
            self._print("Waiting for feedback...")
            if feedback_unlock_cb is not None:
                feedback_unlock_cb()
            self.wait_for_feedback.wait()
            self.wait_for_feedback.clear()
        self._print("Feedback received.")
        self.led.clear_led_all()
        self.dc.set_action(actions.Action.attention_cancel)
        self._print(f"Feedback: {data} => {command} was {self.feedback}")
        self.llm.add_context(data, command, self.feedback)
        if self.feedback:
            if command in self.learned_negatives[data]:
                self.learned_negatives[data].remove(command)
            self.learned_commands[data] = command
            self.total_positives += 1
        else:
            self.learned_negatives[data].append(command)
            # when negative and command was previously learned: remove from learned commands
            if data in self.learned_commands:
                del self.learned_commands[data]
            self.total_negatives += 1
        # reset feedback event
        self.wait_for_feedback.clear()
        # visual feedback feedback
        if self.feedback:
            self.led.start_breathing_color(0.25, self.led.GREEN, self.led.OFF)
        else:
            self.led.start_breathing_color(0.25, self.led.RED, self.led.OFF)
        sleep(3)
        self.led.clear_led_all()
        self.trainer_state_update("Idle", "lightgreen")
        self._print(f"Total positives: {self.total_positives}, Total negatives: {self.total_negatives}", color="lightgreen")
        sleep(2)
    
    def trainer_state_update(self, state: str, color: str = "white"):
        if self.trainer_state_cb is not None:
            self.trainer_state_cb(state, color)
        
    def auto_training(self):
        self.load_all()
        while True:
            self.train_step_event.wait()
            self.train_step_event.clear()
            self.train_step()

    def trigger_train_step(self):
        self.train_step_event.set()

    def stop_all(self):
        self.is_running = False
        self.sr.stop()
        self.llm.stop()
        # set events that might be waited on
        self.sr.data_ready.set()
        self.llm.data_ready.set()
        self.wait_for_feedback.set()

    def print_learned_commands(self):
        self._print("Learned commands:\n" + str(self.learned_commands))
        
    def print_learned_negatives(self):
        self._print("Learned negatives:\n" + str(self.learned_negatives))
        
    def llm_print_preprompt(self):
        if self.loaded["LLM"]:
            self.llm.print_preprompt()
    
    def llm_print_context(self):
        if self.loaded["LLM"]:
            self.llm.print_context()
    
    def is_close_to(self, string_a, string_b):
        return lev.distance(string_a, string_b) < self.LEVENSHTEIN_THRESHOLD

    def find_closest(self, string, string_list):
        min_dist = self.LEVENSHTEIN_THRESHOLD + 1
        closest_string = None
        for s in string_list:
            dist = lev.distance(string, s)
            if dist < min_dist:
                min_dist = dist
                closest_string = s
        return closest_string