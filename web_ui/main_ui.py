import customtkinter as ctk
import _tkinter as tk
from .dog_control_ui import DC_UI
from .SR_ui import SR_UI
from .LLM_ui import LLM_UI

# import TKinter as tk
class MainUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.setup_main_ui()
        sr_ui = SR_UI(self)
        llm_ui = LLM_UI(self)
        dc_ui = DC_UI(self)
        sr_ui.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=5)
        llm_ui.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=5)
        dc_ui.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=5)

    def setup_main_ui(self):
        # change nicegui background color to hexcode "282828"
        self._set_appearance_mode("system")
        self.geometry("1500x800")
        self.title("Main UI")
        main_label = ctk.CTkLabel(self, text="Main UI", font=("Arial", 40))
        main_label.pack(side=ctk.TOP)


# if __name__ in {"__main__", "__mp_main__"}:
#     my_ui = MainUI()
#     # my_ui.mainloop()