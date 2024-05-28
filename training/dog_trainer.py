from custom_speech_recognition import speech_recognition as sr
from custom_llm import llm_api
import enum
import threading as th
import Levenshtein as lev

class t_state(enum.Enum):
    idle = 0
    listening = 1
    thinking = 2
    acting = 3


class dog_trainer:
    def __init__(self, print_callback: callable, sr_model: str):
        self.state = t_state.idle
        self.learned_commands = {}
        self.recognizer = sr.recognizer()
        self._print_cb = print_callback
        self.loaded = [False, False, False]
        self.sr_model = sr_model
        self.train_step_event = th.Event()
        self.wait_for_feedback = th.Event()
        self.feedback: bool = False

    def _print(self, text):
        self._print_cb(text)

    def _load_sr(self):
        model = sr.Model(self.sr_model)
        self.sr: sr.recognizer = sr.recognizer(model, self._print_cb, "german")
        self._print("Finished loading speech recognition.")
        self.loaded[0] = True

    def _load_llm(self):
        self.llm = llm_api.LLM_API(self._print_cb)
        self._print("Finished loading language model.")
        self.loaded[1] = True

    def _load_dc(self):
        pass
        self._print("Finished loading dog controller.")
        self.loaded[2] = True

    def _load_all(self):
        self._print("Loading all...")
        self._print("Loading speech recognition...")
        self._load_sr()
        self._print("Loading language model...")
        self._load_llm()
        self._print("Loading dog controller...")
        self._load_dc()

    def is_all_loaded(self):
        return all(self.loaded)

    def reset_data(self):
        self.learned_commands = {}

    def train_step(self):
        assert self.is_all_loaded(), "Not all components are loaded."
        # Voice recognition
        # start listening and wait for data
        self._print("Triggering voice recognition...")
        self.sr.thread_event.set()
        self.sr.data_ready.wait()
        data = self.sr.data
        self._print("Voice recognition finished.")
        self._print("Recognized: " + data)
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
            if min_dist < 5:
                command = closest_command
                self._print("Found closest command: " + command + " with distance: " + str(min_dist))
        # if prev didn't work: ask llm for command
        if command is None:
            self._print("Asking language model for command...")
            command = self.llm.trigger_prompt(data)
            self.llm.data_ready.wait()
            command = self.llm.prompt_text
            self._print("Language model returned: " + command)
        # execute command

        # get feedback from user
        self._print("Waiting for feedback...")
        self.wait_for_feedback.wait()
        self._print("Feedback received.")
        self._print(f"Feedback: {data} -> {command} was {self.feedback}")
        self.llm.add_context(data, command, self.feedback)
        if self.feedback:
            self.learned_commands[data] = command
        # reset feedback event
        self.wait_for_feedback.clear()
        
    def auto_training(self):
        self._load_all()
        while True:
            self.train_step_event.wait()
            self.train_step_event.clear()
            self.train_step()

    def trigger_train_step(self):
        self.train_step_event.set()
