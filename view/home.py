import tkinter as tk


class HomeFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        from view.database import DatabaseFrame
        from view.schedule import ScheduleFrame

        super().__init__(*args, **kwargs)

        show_schedule = tk.Button(self, text='Schedule', command=lambda: self.master.switch_frame(ScheduleFrame))
        show_schedule.grid(row=0, column=0, padx=20, pady=20, ipadx=20)

        show_schedule = tk.Button(self, text='Database', command=lambda: self.master.switch_frame(DatabaseFrame))
        show_schedule.grid(row=0, column=1, pady=20, ipadx=20)

        greeting_text = tk.Label(self, text='Welcome to the homepage of NARFU University')
        greeting_text.grid(row=0, rowspan=2, columnspan=3)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
