from calendar import c
from cgitb import text
import customtkinter as ctk
import _tkinter as tk
from custom_speech_recognition import speech_recognition as sr
from training.dog_trainer import dog_trainer, t_state
import time
import datetime
import threading as th

# import TKinter as tk
class MainUI(ctk.CTk):
    DD_WIDTH = 200
    HEADER_SIZE = 30
    FONT_SIZE = 20
    PAD_SMALL = 5
    PAD_LARGE = 10

    def __init__(self):
        super().__init__()
        self.dog_trainer: dog_trainer = None
        self.setup_main_ui()
        shared_dict = {}
        self.printed_output = []
        self._epoch = time.time()
        self.output = ""

    def setup_main_ui(self):
        curr_row:int = 0
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
        self.sb_output.grid(row=curr_row, column=0, sticky="nsew", padx=self.PAD_LARGE, pady=self.PAD_LARGE)
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.grid(row=curr_row, column=1, sticky="nsew", padx=self.PAD_LARGE, pady=self.PAD_LARGE)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        # settings and buttons
        input_frame = ctk.CTkFrame(right_frame)
        input_frame.grid(row=curr_row, column=0, sticky="nsew", padx=self.PAD_LARGE, pady=self.PAD_LARGE)
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=1)
        input_label = ctk.CTkLabel(input_frame, text="Settings", font=("Arial", self.HEADER_SIZE))
        input_label.grid(row=curr_row, column=0, columnspan=2, sticky="n", pady=self.PAD_LARGE)
        curr_row += 1
        # input_label.place(relx=0.5, rely=0, anchor=ctk.N)
        # Speech recognition
        sr_model_label = ctk.CTkLabel(input_frame, text="Model:", font=("Arial", self.FONT_SIZE))
        sr_model_label.grid(row=curr_row, column=0, sticky="e", padx=self.PAD_SMALL, pady=self.PAD_SMALL)
        self.dd_model = ctk.CTkOptionMenu(input_frame, values=[model.value for model in sr.Model], font=("Arial", self.FONT_SIZE-1))
        self.dd_model.grid(row=curr_row, column=1, sticky="w", padx=self.PAD_SMALL)
        sr_mic_label = ctk.CTkLabel(input_frame, text="Microphone:", font=("Arial", self.FONT_SIZE))
        curr_row += 1
        ## TODO: Implement microphone selection (optional, since the default microphone is used)
        # sr_mic_label.grid(row=curr_row, column=0, sticky="e", padx=self.PAD_SMALL, pady=self.PAD_SMALL)
        # self.dd_mic = ctk.CTkOptionMenu(input_frame, values=["SR not loaded..."], font=("Arial", self.FONT_SIZE-1))
        # self.dd_mic.grid(row=curr_row, column=1, sticky="w", padx=self.PAD_SMALL)
        # curr_row += 1
        # self.btn_mic_refresh = ctk.CTkButton(input_frame, text="Refresh", font=("Arial", self.FONT_SIZE), command=self.load_mics)
        # self.btn_mic_refresh.grid(row=curr_row, column=1, sticky="w", padx=self.PAD_SMALL)
        # curr_row += 1
        # DC selection
        dc_sel_label = ctk.CTkLabel(input_frame, text="Dog controller:", font=("Arial", self.FONT_SIZE))
        dc_sel_label.grid(row=curr_row, column=0, sticky="e", padx=self.PAD_SMALL, pady=self.PAD_SMALL)
        self.dd_dc = ctk.CTkOptionMenu(input_frame, values=["Pyro_dog", "Dummy"], font=("Arial", self.FONT_SIZE-1))
        self.dd_dc.grid(row=curr_row, column=1, sticky="w", padx=self.PAD_SMALL)
        curr_row += 1
        # buttons init
        self.btn_load_step = ctk.CTkButton(input_frame, text="Load Trainer", font=("Arial", self.FONT_SIZE), command=self.init_trainer)
        self.btn_load_step.grid(row=curr_row, column=0, pady=self.PAD_SMALL,padx=self.PAD_SMALL, sticky="e")
        self.ckb_auto_mode = ctk.CTkCheckBox(input_frame, text="Auto Mode", font=("Arial", self.FONT_SIZE))
        self.ckb_auto_mode.grid(row=curr_row, column=1, pady=self.PAD_SMALL, padx=self.PAD_SMALL, sticky="w")
        curr_row += 1
        # self.btn_load_step.configure(command=self.dog_trainer.train_step)
        # buttons feedback
        self.btn_feedback_pos = ctk.CTkButton(input_frame, text="Feedback +", font=("Arial", self.FONT_SIZE))
        self.btn_feedback_pos.configure(command=lambda: self.send_feebdack(True), state=ctk.DISABLED)
        self.btn_feedback_pos.grid(row=curr_row, column=0, pady=self.PAD_SMALL,padx=self.PAD_SMALL, sticky="e")
        self.btn_feedback_neg = ctk.CTkButton(input_frame, text="Feedback -", font=("Arial", self.FONT_SIZE))
        self.btn_feedback_neg.configure(command=lambda: self.send_feebdack(False), state=ctk.DISABLED)
        self.btn_feedback_neg.grid(row=curr_row, column=1, pady=self.PAD_SMALL,padx=self.PAD_SMALL, sticky="w")
        curr_row += 1
        # buttons debug prints:
        debug_label = ctk.CTkLabel(input_frame, text="Debug prints:", font=("Arial", self.FONT_SIZE))
        debug_label.grid(row=curr_row, column=0, columnspan=2, pady=self.PAD_SMALL)
        self.btn_db_learned = ctk.CTkButton(input_frame, text="Learned", font=("Arial", self.FONT_SIZE), state=ctk.DISABLED)
        curr_row += 1
        self.btn_db_learned.grid(row=curr_row, column=0, pady=self.PAD_SMALL,padx=self.PAD_SMALL, sticky="e")
        self.btn_db_negatives = ctk.CTkButton(input_frame, text="Negatives", font=("Arial", self.FONT_SIZE), state=ctk.DISABLED)
        self.btn_db_negatives.grid(row=curr_row, column=1, pady=self.PAD_SMALL,padx=self.PAD_SMALL, sticky="w")
        self.btn_db_prompt = ctk.CTkButton(input_frame, text="PrePrompt", font=("Arial", self.FONT_SIZE), state=ctk.DISABLED)
        curr_row += 1
        self.btn_db_prompt.grid(row=curr_row, column=0, pady=self.PAD_SMALL,padx=self.PAD_SMALL, sticky="e")
        self.btn_db_context = ctk.CTkButton(input_frame, text="Context", font=("Arial", self.FONT_SIZE), state=ctk.DISABLED)
        self.btn_db_context.grid(row=curr_row, column=1, pady=self.PAD_SMALL,padx=self.PAD_SMALL, sticky="w")
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

    def init_trainer(self):
        self.btn_load_step.configure(state=ctk.DISABLED)
        th.Thread(target=self._init_trainer_async).start()

    def _init_trainer_async(self):
        if self.dog_trainer is None:
            self.dog_trainer : dog_trainer = dog_trainer(self.print_output, self.dd_model.get(), self.update_dog_state_text, self.dd_dc.get())
        else:
            self.dog_trainer.sr_model = self.dd_model.get()
            self.dog_trainer.dog_controller = self.dd_dc.get()
        self.dog_trainer.load_all()
        if not self.dog_trainer.is_all_loaded():
            self.print_output("Not all components of dog_trainer are loaded")
            self.btn_load_step.configure(state=ctk.NORMAL)
            return
        self.btn_load_step.configure(command=self.on_start_button, text="Start Training", state=ctk.NORMAL)
        self.btn_db_learned.configure(command=self.dog_trainer.print_learned_commands, state=ctk.NORMAL)
        self.btn_db_negatives.configure(command=self.dog_trainer.print_learned_negatives, state=ctk.NORMAL)
        self.btn_db_prompt.configure(command=self.dog_trainer.llm_print_preprompt, state=ctk.NORMAL)
        self.btn_db_context.configure(command=self.dog_trainer.llm_print_context, state=ctk.NORMAL)

    def on_start_button(self):
        th.Thread(target=self.training_loop).start()

    def shutdown(self):
        if self.dog_trainer is not None:
            self.dog_trainer.stop_all()

    def unlock_feedback(self):
        self.btn_feedback_pos.configure(state=ctk.NORMAL)
        self.btn_feedback_neg.configure(state=ctk.NORMAL)

    def send_feebdack(self, feedback: bool):
        self.btn_feedback_pos.configure(state=ctk.DISABLED)
        self.btn_feedback_neg.configure(state=ctk.DISABLED)
        self.dog_trainer.feedback = feedback
        self.dog_trainer.wait_for_feedback.set()

    def training_loop(self):
        is_running = True
        while is_running and self.dog_trainer.is_running:
            is_running = False
            self.btn_load_step.configure(state=ctk.DISABLED)
            if self.ckb_auto_mode.get():
                while True:
                    self.dog_trainer.wait_for_hotword()
            self.dog_trainer.train_step(self.unlock_feedback)
            if self.ckb_auto_mode.get():
                is_running = True
        if self.dog_trainer.is_running:                
            self.btn_load_step.configure(state=ctk.NORMAL)

    def print_output(self, text: str, source: str = "UI", color="white"):
        if not self.winfo_exists():
            print("Tried to print to a non-existing window.")
            return
        # Format time as minutes:seconds.ms
        ct = time.time() - self._epoch
        time_stamp = f"{str(int(ct/60)).zfill(3)}:{str(int(ct%60)).zfill(2)}.{str(int(ct*1000)%1000).zfill(3)}"
        output = f"[{time_stamp}|{source}:] {text}"

        label = ctk.CTkLabel(self.sb_output, text=output, font=("Arial", self.FONT_SIZE), text_color=color, justify="left")
        # label.bind("<Configure>", lambda e: label.configure(wraplength=self.sb_output.winfo_width()))
        label.configure(wraplength=self.sb_output.winfo_width())
        label.pack(side=ctk.TOP, anchor="w")
        self.printed_output.append(label)
        self.output += output + "\n"
        print(output)
        self.after(50,self.sb_output._parent_canvas.yview_moveto, 1.0)
        
    def update_dog_state_text(self, state: text):
        if state == "idle":
            self.state_text.configure(text=state, text_color="green")
        else:
            self.state_text.configure(text=state, text_color="yellow")
        
            
# if __name__ in {"__main__", "__mp_main__"}:
#     my_ui = MainUI()
#     # my_ui.mainloop()