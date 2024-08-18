from argparse import Action
from time import sleep

from numpy import add
from sympy import true
import custom_speech_recognition.speech_recognition as sr
import custom_llm.llm_api as llm_api
import enum
import threading as th
import Levenshtein as lev
from collections import defaultdict
import random
import dog_controller.pyro_connector as dc
import dog_controller.actions as actions
import dog_controller.custom_led_lib as led
class t_state(enum.Enum):
    idle = 0
    listening = 1
    thinking = 2
    acting = 3


class dog_trainer:
    LEVENSHTEIN_THRESHOLD = 5
    COMMANDS = [str(action)[7:] for action in actions.Action if action.value > 0]
    COMMANDS = [str(action)[7:] for action in [
        actions.Action.lie_down,
        actions.Action.shake,
        actions.Action.vibe_8,
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
        if data is None or data == "":
            self._print("No voice input received. Cancelling training step...")
            self.trainer_state_update("Idle", "lightgreen")
            self.led.clear_led_all()
            return
        self._print("Voice recognition finished.")
        self._print("Recognized: " + data,color="lightgreen")
        self.trainer_state_update("Checking command...", "yellow")
        # check if command is in confirmed dict
        self._print("Checking if command is in confirmed dict...")
        command = None
        if data in self.learned_commands:
            command = self.learned_commands[data]
            self._print("Found command in confirmed dict: " + command)
        # if prev didn't work: levenshtein distance to find closest command
        if command is None:
            self._print("Command not found in confirmed dict.")
            self._print("Calculating Levenshtein distance...")
            min_dist = 100
            closest_command = None
            for key in self.learned_commands:
                dist = lev.distance(data, key)
                if dist < min_dist:
                    min_dist = dist
                    closest_command = self.learned_commands[key]
            if min_dist < self.LEVENSHTEIN_THRESHOLD:
                command = closest_command
                self._print("Found closest command: " + command + " with distance: " + str(min_dist))
            else:
                self._print(f"No command found with distance < {self.LEVENSHTEIN_THRESHOLD}.")
        # if prev didn't work: ask llm for command
        if command is None:
            self._print("Asking language model for command...")
            self.trainer_state_update("Querying LLM...", "yellow")
            command = self.llm.trigger_prompt(data)
            self.llm.data_ready.wait()
            self.llm.data_ready.clear()
            if not self.sr.is_running:
                print("Cancelled training step.")
                return
            command = self.llm.data
            if command is None:
                # when llm errored out
                self._print("Language model errored out. Cancelling training step...")
                return
            self._print("Language model returned: " + command)
        # when negative command association is currently, roll randomly
        if command in self.learned_negatives[data]:
            old_command = command
            self._print("Command is in negative list. Rolling randomly...", color="red")
            command = self.COMMANDS[random.randint(0, len(self.COMMANDS)-1)]
            self._print(f"Rolled: {old_command} => {command}")
        if command not in self.COMMANDS:
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
            return
        self.dc.set_action(action)
        self._print(f"Waiting for idle from dog controller...")
        self.dc.wait_for_idle.clear()
        self.dc.wait_for_idle.wait()
        self.dc.wait_for_idle.clear()
        self.dc.set_action(actions.Action.attention)
        # get feedback from user
        self._print("Waiting for feedback from user", "yellow")
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
                if "gut" in self.sr.data.lower() or "gemacht" in self.sr.data.lower():
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
            self.led.breath_single_color(self.led.YELLOW)
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
        else:
            self.learned_negatives[data].append(command)
            # when negative and command was previously learned: remove from learned commands
            if data in self.learned_commands:
                del self.learned_commands[data]
        # reset feedback event
        self.wait_for_feedback.clear()
        self.trainer_state_update("Idle", "lightgreen")
    
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
            