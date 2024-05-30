import time
import enum
import speech_recognition as sr
import threading as th
class Model(enum.Enum):
    """Enum for different models of the speech recognition library."""
    W_T = "Whisper tiny"
    W_D = "Whisper default"
    W_L = "Whisper large"

class recognizer():
    def __init__(self, model:Model, print_callback: callable, language: str) -> None:
        self.print_callback = print_callback
        self.model = model
        self.language = "german"
        self.r = sr.Recognizer()
        self.thread_event = th.Event()
        self.data_ready = th.Event()
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
        self.thread_event.clear()
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
        match model:
            case Model.W_T:
                m_method = self.r.recognize_whisper
                m_name = "tiny"
            case Model.W_D:
                m_method = self.r.recognize_whisper
                m_name = "base"
            case Model.W_L:
                m_method = self.r.recognize_whisper
                m_name = "large"
            case _:
                raise ValueError("Model not found")
        return m_method, m_name

    def listen_auto(self,  timeout: int = 5, model_override: Model = None):
        try:
            with sr.Microphone() as source:
                self._print("Listening...")
                audio = self.r.listen(source, timeout=timeout)
                self._print("Processing...")
        except sr.exceptions.WaitTimeoutError:
            self._print("Timeout error, cancelled listening.")
            self.data = ""
            return
        start_time = time.time()
        model = model_override if model_override else self.model
        m_method, m_name = self.match_model(model)
        try:
            self._print(f"Recognizing using {model.value} model...")
            self._print(f"model: {m_name}, language: {self.language}")
            text = m_method(audio, model=m_name, language="german")
            # text = m_method(audio)
            # text = self.r.recognize_whisper(audio)
            self.data = text
        except sr.UnknownValueError:
            self._print("Could not understand audio")
            self.data = ""
        except sr.RequestError as e:
            self._print(f"Could not request results; {e}")
            self.data = ""
        finally:
            self._print(f"Time elapsed: {time.time() - start_time}")
