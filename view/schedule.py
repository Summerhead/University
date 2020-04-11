import tkinter as tk
import calendar
import datetime

info = ''


class EditDayButton(tk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(command=self.create_window)

    def create_window(self):
        self.edit_window = tk.Toplevel()

        name_label = tk.Label(self.edit_window, text='name:')
        name_label.place(x=10, y=10)

        self.name = tk.Text(self.edit_window, height=0, width=10)
        self.name.place(x=50, y=10)

        ok_button = tk.Button(self.edit_window, text='OK', command=self._send_info)
        ok_button.place(x=25, y=25)

    def _send_info(self):
        global info
        name_val = self.name.get('1.0', 'end')

        info = name_val
        print(info)

        subject_frame = tk.LabelFrame(self.master, width=150, height=100)
        subject_frame.grid(row=1, column=0)

        name_label_schedule = tk.Label(self.master, text=info)
        name_label_schedule.grid(row=1, column=0)

        subject_frame = tk.LabelFrame(self.master, width=150, height=100)
        subject_frame.grid(row=2, column=0)

        name_label_schedule = tk.Label(self.master, text=info)
        name_label_schedule.grid(row=2, column=0)

        subject_frame = tk.LabelFrame(self.master, width=150, height=100)
        subject_frame.grid(row=3, column=0)

        name_label_schedule = tk.Label(self.master, text=info)
        name_label_schedule.grid(row=3, column=0)

        self.edit_window.destroy()


class VerticalScrolledFrame(tk.LabelFrame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """

    def __init__(self, parent, *args, **kw):
        tk.LabelFrame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient='vertical')
        vscrollbar.pack(fill='y', side='right', expand=False)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor='nw')

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth(), height=interior.winfo_reqheight())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)


class ScheduleFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        from view.home import HomeFrame

        super().__init__(*args, **kwargs)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        back = tk.Button(self, text='Back', command=lambda: self.master.switch_frame(HomeFrame))
        back.grid(row=0, column=0, padx=40, pady=20, sticky='n')

        sch = tk.LabelFrame(self, text='Schedule')
        sch.grid(row=0, column=1, padx=10, pady=10)
        sch.rowconfigure(1, weight=1)

        days_area = tk.LabelFrame(sch)

        day_names = calendar.day_name
        for i in range(len(day_names)):
            tk.Label(days_area, text=day_names[i]).grid(row=0, column=i)
            days_area.grid_columnconfigure(i, weight=1, uniform="fred")

        days_area.pack(fill='x', expand=True, padx=(0, 20))

        frame = VerticalScrolledFrame(sch)
        frame.pack()

        schedule_area = tk.Frame(frame.interior)

        today = datetime.datetime.today()
        monthrange = calendar.monthrange(today.year, today.month)
        first_day = monthrange[0]
        num_of_days = monthrange[1]

        row_num = 1
        column_num = first_day

        for i in range(num_of_days):
            days_area = tk.LabelFrame(schedule_area, text=i + 1, width=150, height=150)
            days_area.grid(row=row_num, column=column_num, padx=2, pady=2, sticky='n')
            days_area.grid_propagate(1)

            edit_button = EditDayButton(days_area, text='Edit')
            edit_button.place(x=115)

            days_area.columnconfigure(0, weight=1)

            column_num += 1
            if column_num == 7:
                column_num = 0
                row_num += 1

        schedule_area.pack()
