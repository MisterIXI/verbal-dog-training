import requests
import time


class LLM_API:
    def __init__(self, print_callback: callable, commands: list[str] = ["platz", "tanzen", "maennchen"], obfuscate_names: bool = True) -> None:
        self.print_cb = print_callback
        self.url = "http://localhost:8080/completion"
        self.obfuscate_names = obfuscate_names
        self.grammar = self.build_grammar(commands, self.obfuscate_names)
        self.print("Grammar: " + self.grammar)
        self.context = []
        self.commands = commands
        self.preprompt = self._get_preprompt()
        self.add_context("platz", "platz", True)
        self.add_context("beweg dich", "maennchen", False)
        self.add_context("runter", "platz", True)
        self.add_context("tanzen", "tanzen", True)
        self.add_context("runter", "maennchen", False)
        self.add_context("maennchen", "maennchen", True)
        self.add_context("beweg dich", "tanzen", True)

    def print(self, text: str):
        self.print_cb(text)

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
        self.context.append(f"{"{"}{prompt}: {command}: {correct}{"}"}")

    def prompt(self, text: str, print_prompt: bool = True) -> str:
        self.print("Prompting with: " + text)
        payload = self._create_payload(
            self.preprompt, self.context, text, print_prompt=print_prompt)
        start_time = time.time()
        response = requests.post(self.url, json=payload)
        responses = []
        for i in range(1):
            response = requests.post(self.url, json=payload)
            responses.append(response)
        # print("Responses: " + str([r.json()["content"] for r in responses]))
        time_taken = time.time() - start_time
        self.print_cb(f"Time taken: {round(time_taken, 3)}")
        if response.status_code == 200:
            response_json = response.json()
            chosen_command = response_json["content"]
            if self.obfuscate_names:
                chosen_command += " (de-obfuscated: " + \
                    self.commands[int(chosen_command[-1]) - 1] + ")"
            self.print_cb(f"Response: {chosen_command}")
            return response_json["content"]
        else:
            self.print_cb(f"Request failed...")
            raise ValueError("Request failed: " + response.text)

    def _reset_and_fill_context(self):
        self.context = []

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
                return "This is a conversation between User and Llama, a precise and friendly chatbot designed to execute commands accurately based on context.\n\
                Llama analyzes past commands and current prompts to determine the most appropriate action to take. Each command provided in the context will be associated with its correctness.\n\
                The context provided will have the following format: {prompt: command: correct}\n\
                Prompt: The text presented to Llama.\n\
                Command: The action chosen by Llama.\n\
                Correct: A boolean indicating whether the chosen action was correct or not.\n\
                The possible commands are: [platz, tanzen, maennchen]\n\
                - {platz: platz: True} - The user said 'platz', Llama chose 'platz', and this was the correct action.\n\
                - {beweg dich: maennchen: False} - The user said 'beweg dich', Llama chose 'maennchen', but this was not the correct action.\n\
                - {runter: platz: True} - The user said 'runter', Llama chose 'platz', and this was the correct action.\n\
                - {tanzen: tanzen: True} - The user said 'tanzen', Llama chose 'tanzen', and this was the correct action.\n\
                Here is the context provided to Llama:\n"
            case _:
                raise ValueError("Invalid id")

    def _create_payload(self, pre_prompt: str, context: list[str], prompt: str, print_prompt: bool = False) -> str:
        context_str = ""
        for c in context:
            context_str += c + "\n"
        prompt_str = "User: " + prompt + "\n"
        response_str = "Llama: "
        if print_prompt:
            print("Prompt: " + pre_prompt + context_str + prompt_str + response_str)
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
