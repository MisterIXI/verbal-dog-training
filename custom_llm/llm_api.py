import random
import requests
import time
import threading as th


class LLM_API:
    def __init__(self, print_callback: callable, commands: list[str] = ["platz", "tanzen", "maennchen"], obfuscate_names: bool = True) -> None:
        self.print_callback = print_callback
        self.url = "http://localhost:8080/completion"
        self.obfuscate_names = obfuscate_names
        self.grammar = self.build_grammar(commands, self.obfuscate_names)
        # self.print_cb("Grammar: " + self.grammar)
        self.context = {}
        self.commands = commands
        self.preprompt = self._get_preprompt()
        for i in range(5):
            # add 5 random context entries
            a = random.choice(commands)
            b = random.choice(commands)
            self.add_context(a, b, a == b)
        self.is_running = True
        self.prompt_event = th.Event()
        self.data_ready = th.Event()
        self.prompt_text = ""

    def _print(self, text: str, source: str = "LLM_API", color="white"):
        self.print_callback(text, source, color)

    def build_grammar(self, commands: list[str], obfuscate_names: bool = True) -> str:
        x = "root ::= "
        command_count = len(commands)
        for i, command in enumerate(commands):
            x += f"command{i+1}"
            if i < command_count - 1:
                x += " | "
        x += "\n"
        for i, command in enumerate(commands):
            x += f"command{i+1} ::= \""
            if obfuscate_names:
                x += f"command{i+1}"
            else:
                x += f"{command}"
            x += "\"\n"
        return x

    def add_context(self, prompt: str, command: str, correct: bool) -> None:
        self.context[prompt] = (command, correct)

    def stop(self):
        self.is_running = False
        self.prompt_event.set()

    def trigger_prompt(self, prompt: str):
        self.prompt_text = prompt
        self.prompt_event.set()

    def test_if_running(self) -> bool:
        payload = self._create_payload("", {}, "test", print_prompt=False)
        try:
            response = requests.post(self.url, json=payload)
        except requests.exceptions.ConnectionError:
            return False
        return response.status_code == 200

    def prompt(self):
        self.data_ready.clear()
        self.prompt_event.clear()
        self._print("Started up and waiting for prompt...")
        while self.is_running:
            self.prompt_event.wait()
            self.prompt_event.clear()
            if not self.is_running:
                break
            if self.prompt_text == "":
                self._print("Prompt text is empty...")
            else:
                self._print("Prompt received!")
            self.data_ready.clear()
            self._print("Prompting with: " + self.prompt_text, color="yellow")
            payload = self._create_payload(
                self.preprompt, self.context, self.prompt_text, print_prompt=True)
            start_time = time.time()
            try:
                response = requests.post(self.url, json=payload)
            except requests.exceptions.ConnectionError:
                # when the server is not running
                self._print("Could not query the LLM server. Is it running?")
                self.data = None
                self.data_ready.set()
                continue
            # print("Responses: " + str([r.json()["content"] for r in responses]))
            time_taken = time.time() - start_time
            self._print(f"Time taken: {round(time_taken, 3)}")
            if response.status_code == 200:
                response_json = response.json()
                chosen_command = response_json["content"]
                if self.obfuscate_names:
                    chosen_command += " (de-obfuscated: " + \
                        self.commands[int(chosen_command[-1]) - 1] + ")"
                self._print(f"Response: {chosen_command}")
                self.data = response_json["content"]
                self.data_ready.set()
            else:
                self._print(f"Request failed...")
                self.data = None
                self.data_ready.set()
                raise ValueError("Request failed: " + response.text)

    def _reset_and_fill_context(self):
        self.context = {}

    def _get_preprompt(self, id: int = 2) -> str:
        command_prompt = "The possible commands are: ["
        for i, command in enumerate(self.commands):
            if self.obfuscate_names:
                command_prompt += f"command{i+1}"
            else:
                command_prompt += f"{command}"
            if i < len(self.commands) - 1:
                command_prompt += ", "
        command_prompt += "]\n"
        match id:
            case 1:
                return "This is a conversation between User and Llama, a friendly and precise chatbot. Llama is a precise LLM, which takes context of old commands and actions together with the current command to figure out one action to execute. It never fails to answer prompts with the best possible option with the provided context.\nThe context provided will have the following formate: {prompt: command: correct}\nPrompt is the text that was prompted to Llama, command is the command that was chosen by Llama and correct is a boolean value that tells if the command chosen was correct or not.\n" + command_prompt
            case 2:
                return "This is a conversation between User and Llama, a precise chatbot designed to execute commands accurately based on context.\n\
                Llama analyzes past commands and current prompts to determine the most appropriate action to take. Each command provided in the context will be associated with its correctness.\n\
                The context provided will have the following format: {prompt: command: correct}\n\
                Prompt: The text presented to Llama.\n\
                Command: The action chosen by Llama.\n\
                Correct: A boolean indicating whether the chosen action was correct or not.\n\
                - {platz: platz: True} - The user said 'platz', Llama chose 'platz', and this was the correct action.\n\
                - {beweg dich: maennchen: False} - The user said 'beweg dich', Llama chose 'maennchen', but this was not the correct action.\n\
                - {runter: platz: True} - The user said 'runter', Llama chose 'platz', and this was the correct action.\n" + command_prompt
            case _:
                raise ValueError("Invalid id")
    def _build_context(self, context: dict) -> str:
        context_str = ""
        for c in context:
            command, correct = context[c]
            context_str += f"{{{c}, {command}, {correct}}}" + "\n"
        return context_str
    
    def _create_payload(self, pre_prompt: str, context: dict, prompt: str, print_prompt: bool = False) -> str:
        context_str = self._build_context(context)
        prompt_str = "User: " + prompt + "\n"
        response_str = "Llama: "
        if print_prompt:
            print("Prompt: " + pre_prompt +
                  context_str + prompt_str + response_str)
        return {
            "stream": False,
            "n_predict": 15,
            "temperature": 0.7,
            "stop": ["</s>",
                     "Llama:",
                     "User:"],
            "repeat_last_n": 256,
            "repeat_penalty": 1.18,
            "penalize_nl": False,
            "top_k": 40,
            "top_p": 0.95,
            "min_p": 0.05,
            "tfs_z": 1,
            "typical_p": 1,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "mirostat": 2,
            "mirostat_tau": 5,
            "mirostat_eta": 0.1,
            "grammar": self.grammar,
            "n_probs": 7,
            "min_keep": 0,
            "image_data": [],
            "cache_prompt": True,
            "api_key": "",
            "slot_id": -1,
            "prompt": pre_prompt + context_str + prompt_str
        }

    def print_preprompt(self):
        self._print("LLM Prepromt:\n" + self.preprompt)
    
    def print_context(self):
        self._print("LLM Context:\n" + self._build_context(self.context))
