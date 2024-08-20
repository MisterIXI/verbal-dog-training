import time
import enum
import speech_recognition as sr
import threading as th


class Model(enum.Enum):
    """Enum for different models of the speech recognition library."""
    W_Tiny = "WH_tiny"
    W_Base = "WH_base"
    W_Small = "WH_small"
    W_Medium = "WH_medium"
    W_Large = "WH_large"
    # Vosk = "Vosk"


class recognizer():
    def __init__(self, model: Model, print_callback: callable, language: str) -> None:
        self.print_callback = print_callback
        self.model = model
        self.language = "german"
        self.r = sr.Recognizer()
        self.thread_event = th.Event()
        self.data_ready = th.Event()
        self.finished_listening = th.Event()
        self.is_running = True
        self.init_model()

    def init_model(self):
        try:
            with sr.Microphone() as source:
                audio = self.r.record(source, duration=0.1)
            method, name = self.match_model(self.model)
            method(audio, model=name, language=self.language)
        except Exception as e:
            pass

    def stop(self):
        self.is_running = False
        self.thread_event.set()

    def _print(self, text: str, source: str = "SR", color="white"):
        self.print_callback(text, source, color)

    def run(self):
        """When self.thread_event is set, listen for audio and recognize it in one step, then set self.data_ready once the data is ready."""
        self.init_model()
        self.data_ready.clear()
        while self.is_running:
            # wait for thread event
            self.thread_event.wait()
            self.thread_event.clear()
            if not self.is_running:
                break
            # reset data and data flag
            self.data_ready.clear()
            self.data = None
            # listen for audio and recognize it in one step
            self.listen_auto()
            # set data flag to indicate that data is ready
            self.data_ready.set()

    def match_model(self, model: Model) -> tuple[callable, str]:
        # match model:
        if model == Model.W_Tiny:
            # case Model.W_T:
            m_method = self.r.recognize_whisper
            m_name = "tiny"
            # case Model.W_D:
        elif model == Model.W_Base:
            m_method = self.r.recognize_whisper
            m_name = "base"
            # case Model.W_L:
        elif model == Model.W_Small:
            m_method = self.r.recognize_whisper
            m_name = "small"
        elif model == Model.W_Medium:
            m_method = self.r.recognize_whisper
            m_name = "medium"
        elif model == Model.W_Large:
            m_method = self.r.recognize_whisper
            m_name = "large"
            # case _:
        # elif model == Model.Vosk:
        #     m_method = self.r.recognize_vosk
        #     m_name = ""
        else:
            raise ValueError("Model not found")
        return m_method, m_name

    def listen_auto(self,  timeout: int = 5, phrase_timelimit: int | None = 5, model_override: Model = None):
        try:
            with sr.Microphone() as source:
                self._print("Listening...")
                audio = self.r.listen(source, timeout=timeout, phrase_time_limit=phrase_timelimit)
                self._print("Processing...")
        except sr.exceptions.WaitTimeoutError:
            self._print("Timeout error, cancelled listening.")
            self.data = ""
            self.finished_listening.set()
            self.data_ready.set()
            return
        self.finished_listening.set()
        start_time = time.time()
        model = model_override if model_override else self.model
        m_method, m_name = self.match_model(model)
        try:
            self._print(f"Recognizing using {model.value} model...")
            self._print(f"model: {m_name}, language: {self.language}")
            if m_name == "":
                text = m_method(audio, language=self.language)
            else:
                text = m_method(audio, model=m_name, language=self.language)
            # text = m_method(audio)
            # text = self.r.recognize_whisper(audio)
            self.data = text
        except sr.UnknownValueError:
            self._print("Could not understand audio")
            self.data = ""
        except sr.RequestError as e:
            self._print(f"Could not request results; {e}")
            self.data = ""
        # except TypeError as e:
        #     self._print(f"Error in recognizing audio; {e}")
        #     self._print("Error in recognizing audio")
        #     self.data = ""
        finally:
            self._print(f"Time elapsed: {time.time() - start_time}")
