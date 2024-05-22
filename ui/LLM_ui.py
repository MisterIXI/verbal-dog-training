import customtkinter as ctk
from custom_llm import llm_api as llm

class LLM_UI(ctk.CTkFrame):
    def __init__(self, master, shared_dict: dict):
        super().__init__(master)
        title = ctk.CTkLabel(self, text="LLM UI", font=("Arial", 40))
        title.pack(side=ctk.TOP)
        self.shared_dict = shared_dict
        self.scrollbox = ctk.CTkScrollableFrame(self)
        self.btn_frame = ctk.CTkFrame(self, fg_color=None)
        self.btn_frame.pack(side=ctk.TOP, anchor=ctk.N, pady=10)
        self.eb_command = ctk.CTkEntry(self.btn_frame)
        self.eb_command.bind("<Return>", lambda e: self._command())
        self.eb_command.pack(in_=self.btn_frame, side=ctk.LEFT, padx=5, anchor=ctk.N)
        self.bt_send = ctk.CTkButton(self.btn_frame, text="Send", command=self._command)
        self.bt_send.pack(in_=self.btn_frame, side=ctk.LEFT, padx=5, anchor=ctk.N)
        self.scrollbox.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, pady=10)
        self.after(150,self._load)
    
    def _command(self ):
        command = self.eb_command.get()
        self.eb_command.delete(0, ctk.END)
        self.llm.prompt(command)

    def _load(self):
        self.wraplength = self.scrollbox.winfo_width()
        self.llm = llm.LLM_API(self._print_cb, obfuscate_names=False)
        self.shared_dict["llm"] = self.llm

    def _print_cb(self, text):
        print(text)
        lb = ctk.CTkLabel(self.scrollbox, text=text, wraplength=self.wraplength)
        lb.pack(side=ctk.TOP)
        
        self.after(50,self.scrollbox._parent_canvas.yview_moveto, 1.0)

