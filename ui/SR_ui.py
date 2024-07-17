import customtkinter as ctk
import enum
from custom_speech_recognition import speech_recognition as sr
# enum for models
class SR_UI(ctk.CTkFrame):
    def __init__(self, master, shared_dict: dict):
        super().__init__(master)
        title = ctk.CTkLabel(self, text="SR UI", font=("Arial", 40))
        title.pack(side=ctk.TOP)
        btn_frame = ctk.CTkFrame(self, fg_color=None)
        self.btn_frame = btn_frame
        self.shared_dict = shared_dict
        # self.btn_frame.place(relx=0.5, rely=0.5, anchor=ctk.N)
        self.btn_frame.pack(side=ctk.TOP, anchor=ctk.N, pady=10)
        self.bt_start = ctk.CTkButton(btn_frame, text="Load", command=self.load)
        self.bt_start.pack(in_=btn_frame, side=ctk.LEFT, padx=5, anchor=ctk.N)
        lb_model = ctk.CTkLabel(btn_frame, text="Model:")
        lb_model.pack(in_=btn_frame, side=ctk.LEFT, padx=5, anchor=ctk.N)
        self.dd_model = ctk.CTkOptionMenu(btn_frame, values=[model.value for model in sr.Model])
        self.dd_model.pack(in_=btn_frame, side=ctk.LEFT, padx=5, anchor=ctk.N)
        self.scrollbox = ctk.CTkScrollableFrame(self)
        self.scrollbox.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, pady=10)
        # btn_frame.pack(side=ctk.TOP, anchor=ctk.CENTER)

    def load(self):
        model = sr.Model(self.dd_model.get())
        self.wraplength = self.scrollbox.winfo_width()
        self.sr : sr.recognizer = sr.recognizer(model, self._print_cb, "german")
        self.bt_start.configure(text="Start", command=self.start)
        self.shared_dict["sr"] = self.sr

    def start(self):
        self.sr.listen_auto(self._print_cb, model_override=sr.Model(self.dd_model.get()))

    def stop(self):
        pass

    def _print_cb(self, text):
        print(text)
        lb = ctk.CTkLabel(self.scrollbox, text=text, wraplength=self.wraplength)
        lb.pack(side=ctk.TOP)
        
        self.after(50,self.scrollbox._parent_canvas.yview_moveto, 1.0)
