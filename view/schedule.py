import tkinter as tk
import calendar
import datetime

from view.database import set_entry_text


class VerticalScrolledFrame(tk.LabelFrame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """

    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw)

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
        from db_model.database import Database

        super().__init__(*args, **kwargs)

        self.database = Database()

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.configure_widget()

    def configure_widget(self):
        from view.home import HomeFrame

        back = tk.Button(self, text='Back', command=lambda: self.master.switch_frame(HomeFrame))
        back.grid(row=0, column=0, padx=40, pady=20, sticky='n')

        schedule_frame = tk.LabelFrame(self, text='Schedule')
        schedule_frame.grid(row=0, column=1, padx=10, pady=10)
        schedule_frame.rowconfigure(1, weight=1)

        days_area = tk.LabelFrame(schedule_frame)

        day_names = calendar.day_name
        for i in range(len(day_names)):
            tk.Label(days_area, text=day_names[i]).grid(row=0, column=i)
            days_area.grid_columnconfigure(i, weight=1, uniform="fred")

        days_area.pack(fill='x', expand=True, padx=(0, 20))

        vs_frame = VerticalScrolledFrame(schedule_frame)
        vs_frame.pack()

        schedule_area = tk.Frame(vs_frame.interior)

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

            edit_button = tk.Button(days_area, text='Edit',
                                    command=lambda: DayWindow(parent=self, database=self.database))
            edit_button.place(x=115)

            days_area.columnconfigure(0, weight=1)

            column_num += 1
            if column_num == 7:
                column_num = 0
                row_num += 1

        schedule_area.pack()


class DayWindow(tk.Toplevel):
    def __init__(self, parent=None, database=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent = parent
        self.database = database
        self.label_names = ['Time', 'Classroom', 'Address', 'Subject', 'Teacher', 'Type']
        self.entities = ['Classroom', 'Subject', 'Teacher']
        self.day_frames = []
        self.entries = []

        self.configure_widget()

        for slave in self.grid_slaves():
            if slave.grid_info()['column'] == 2:
                print(slave, slave.grid_info()['row'])

    def configure_widget(self):
        from view.database import OptionMenuRelation

        day_frame = tk.Frame(self)
        day_frame.grid(row=0, column=0)

        last_row = 0
        for row, name in enumerate(self.label_names):
            tk.Label(day_frame, text=name).grid(row=row, column=0)

            entry = tk.Entry(day_frame)
            entry.grid(row=row, column=1)
            self.entries.append(entry)

            if name in self.entities:
                drop_down = OptionMenuRelation(parent=day_frame, folder='entity', entity=name.lower(),
                                               database=self.database, row=row, column=2)
                id_name_map = drop_down.id_name_map
                menu = drop_down.menu

                for option in id_name_map:
                    menu.add_command(label=id_name_map.get(option),
                                     command=lambda value=id_name_map.get(option),
                                                    entry_=entry: set_entry_text(entry_, value))
            last_row = row

        tk.Button(day_frame, text='OK', command=lambda: self.create_classes()).grid(row=last_row + 1, column=0)

    def create_classes(self):
        classroom = self.grid_slaves(row=0, column=0)
        subject = self.grid_slaves(row=1, column=0)
        type_ = self.grid_slaves(row=2, column=0)
        teacher = self.grid_slaves(row=3, column=0)

        self.destroy()
