import speech_recognition as sr
import time
import enum

class Model(enum.Enum):
    W_T = "Whisper tiny"
    W_D = "Whisper default"
    W_L = "Whisper large"

class recognizer():
    def __init__(self, model:Model, print_callback: callable, language: str) -> None:
        self.print_cb = print_callback
        self.model = model
        self.language = "german"
        self.r = sr.Recognizer()
    
    def listen_auto(self, callback: callable, timeout: int = 5, model_override: Model = None):
        pass
        with sr.Microphone() as source:
            self.print_cb("Listening...")
            audio = self.r.listen(source, timeout=timeout)
            self.print_cb("Processing...")
        start_time = time.time()
        model = model_override if model_override else self.model
        m_method: callable = None
        m_name: str = None
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
        try:
            self.print_cb(f"Recognizing using {model.value} model...")
            self.print_cb(f"model: {m_name}, language: {self.language}")
            text = m_method(audio, model=m_name, language="german")
            # text = m_method(audio)
            # text = self.r.recognize_whisper(audio)
            callback(text)
        except sr.UnknownValueError:
            self.print_cb("Could not understand audio")
        except sr.RequestError as e:
            self.print_cb(f"Could not request results; {e}")
        finally:
            self.print_cb(f"Time elapsed: {time.time() - start_time}")

                

