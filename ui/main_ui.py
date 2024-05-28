import customtkinter as ctk
import _tkinter as tk
from .dog_control_ui import DC_UI
from .SR_ui import SR_UI
from .LLM_ui import LLM_UI
from custom_speech_recognition import speech_recognition as sr


# import TKinter as tk
class MainUI(ctk.CTk):
    DD_WIDTH = 200
    HEADER_SIZE = 30
    FONT_SIZE = 20
    PAD_SMALL = 5
    PAD_LARGE = 10

    def __init__(self):
        super().__init__()
        self.setup_main_ui()
        shared_dict = {}

    def setup_main_ui(self):
        # change nicegui background color to hexcode "282828"
        self._set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.geometry("1500x800")
        self.title("Dog Training")
        main_label = ctk.CTkLabel(self, text="Dog Training", font=("Arial", 40))
        main_label.pack(side=ctk.TOP, pady=self.PAD_LARGE)        
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(side=ctk.BOTTOM, fill=ctk.BOTH, expand=True, padx=self.PAD_LARGE, pady=self.PAD_LARGE)
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        self.sb_output = ctk.CTkScrollableFrame(content_frame)
        self.sb_output.grid(row=0, column=0, sticky="nsew", padx=self.PAD_LARGE, pady=self.PAD_LARGE)
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=self.PAD_LARGE, pady=self.PAD_LARGE)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        # settings and buttons
        input_frame = ctk.CTkFrame(right_frame)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=self.PAD_LARGE, pady=self.PAD_LARGE)
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=1)
        input_label = ctk.CTkLabel(input_frame, text="Settings", font=("Arial", self.HEADER_SIZE))
        input_label.grid(row=0, column=0, columnspan=2, sticky="n", pady=self.PAD_LARGE)
        # input_label.place(relx=0.5, rely=0, anchor=ctk.N)
        # Speech recognition
        sr_model_label = ctk.CTkLabel(input_frame, text="Model:", font=("Arial", self.FONT_SIZE))
        sr_model_label.grid(row=1, column=0, sticky="e", padx=self.PAD_SMALL, pady=self.PAD_SMALL)
        self.dd_model = ctk.CTkOptionMenu(input_frame, values=[model.value for model in sr.Model], font=("Arial", self.FONT_SIZE),width=self.DD_WIDTH)
        self.dd_model.grid(row=1, column=1, sticky="w", padx=self.PAD_SMALL)
        sr_mic_label = ctk.CTkLabel(input_frame, text="Microphone:", font=("Arial", self.FONT_SIZE))
        sr_mic_label.grid(row=2, column=0, sticky="e", padx=self.PAD_SMALL, pady=self.PAD_SMALL)
        self.dd_mic = ctk.CTkOptionMenu(input_frame, values=["Default", "None"], font=("Arial", self.FONT_SIZE),width=self.DD_WIDTH)
        self.dd_mic.grid(row=2, column=1, sticky="w", padx=self.PAD_SMALL)

        # dog state
        dogstate_frame = ctk.CTkFrame(right_frame)
        dogstate_frame.grid(row=1, column=0, sticky="nsew", padx=self.PAD_LARGE, pady=self.PAD_LARGE)
        dogstate_frame.grid_columnconfigure(0, weight=1)
        dogstate_frame.grid_columnconfigure(1, weight=1)
        state_title = ctk.CTkLabel(dogstate_frame, text="Dog State", font=("Arial", self.HEADER_SIZE))
        state_title.grid(row=0, column=0, columnspan=2, pady=self.PAD_LARGE)
        state_label = ctk.CTkLabel(dogstate_frame, text="Dog state:", font=("Arial", self.FONT_SIZE))
        state_label.grid(row=1, column=0,sticky="e")
        self.state_text = ctk.CTkLabel(dogstate_frame, text="Idle", font=("Arial", self.FONT_SIZE))
        self.state_text.grid(row=1, column=1, sticky="w",padx=self.PAD_SMALL)
        self.state_text.configure(text_color="green")
# if __name__ in {"__main__", "__mp_main__"}:
#     my_ui = MainUI()
#     # my_ui.mainloop()