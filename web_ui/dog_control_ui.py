import customtkinter as ctk


class DC_UI(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        title = ctk.CTkLabel(self, text="Dog Control UI", font=("Arial", 40))
        title.pack(side=ctk.TOP)
        
        