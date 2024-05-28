import customtkinter as ctk
import _tkinter as tk
from .dog_control_ui import DC_UI
from .SR_ui import SR_UI
from .LLM_ui import LLM_UI
from custom_speech_recognition import speech_recognition as sr
# import TKinter as tk
class MainUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.setup_main_ui()
        shared_dict = {}

        

    def setup_main_ui(self):
        # change nicegui background color to hexcode "282828"
        self._set_appearance_mode("system")
        self.geometry("1500x800")
        self.title("Dog Training")
        main_label = ctk.CTkLabel(self, text="Dog Training", font=("Arial", 40))
        main_label.pack(side=ctk.TOP)        
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(side=ctk.BOTTOM, fill=ctk.BOTH, expand=True, padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        self.sb_output = ctk.CTkScrollableFrame(content_frame)
        self.sb_output.grid(row=0, column=0, sticky="nsew", padx = 10, pady = 10)
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx = 10, pady = 10)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        # settings and buttons
        input_frame = ctk.CTkFrame(right_frame)
        input_frame.grid(row=0, column=0, sticky="nsew", padx = 10, pady = 10)
        input_label = ctk.CTkLabel(input_frame, text="Settings", font=("Arial", 20))
        input_label.grid(row=0, column=0, columnspan=2)
        # Speech recognition
        sr_model_label = ctk.CTkLabel(input_frame, text="Model:", font=("Arial", 15))
        sr_model_label.grid(row=1, column=0, sticky="ew")
        self.dd_model = ctk.CTkOptionMenu(input_frame, values=[model.value for model in sr.Model])
        self.dd_model.grid(row=1, column=1, sticky="ew", pady=5)
        sr_mic_label = ctk.CTkLabel(input_frame, text="Microphone:", font=("Arial", 15))
        sr_mic_label.grid(row=2, column=0, sticky="ew")
        self.dd_mic = ctk.CTkOptionMenu(input_frame, values=["Default", "None"])
        self.dd_mic.grid(row=2, column=1, sticky="ew")
        # dog state
        dogstate_frame = ctk.CTkFrame(right_frame)
        dogstate_frame.grid(row=1, column=0, sticky="nsew", padx = 10, pady = 10)
        dogstate_frame.grid_columnconfigure(0, weight=1)
        dogstate_frame.grid_columnconfigure(1, weight=1)
        state_title = ctk.CTkLabel(dogstate_frame, text="Dog State", font=("Arial", 20))
        state_title.grid(row=0, column=0, columnspan=2)
        state_label = ctk.CTkLabel(dogstate_frame, text="Dog state:", font=("Arial", 15))
        state_label.grid(row=1, column=0)
        self.state_text = ctk.CTkLabel(dogstate_frame, text="Idle", font=("Arial", 15))
        self.state_text.grid(row=1, column=1)
        self.state_text.configure(text_color="green")
# if __name__ in {"__main__", "__mp_main__"}:
#     my_ui = MainUI()
#     # my_ui.mainloop()