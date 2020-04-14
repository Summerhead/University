import calendar
import datetime
import tkinter as tk

from entity.entity.school_class import SchoolClass
from view.database import set_entry_text, multi_functions


class VerticalScrolledFrame(tk.LabelFrame):
    """
    A pure Tkinter scrollable frame that actually works!
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
            canvas.config(scrollregion='0 0 %s %s' % size)
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
        self.database.open_database('entity', 'school_class')

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

        day_names_area = tk.LabelFrame(schedule_frame)

        day_names = calendar.day_name

        for num, day_name in enumerate(day_names):
            tk.Label(day_names_area, text=day_name).grid(row=0, column=num)
            day_names_area.grid_columnconfigure(num, weight=1, uniform='fred')

        day_names_area.pack(fill='x', expand=True, padx=(0, 20))

        vs_frame = VerticalScrolledFrame(schedule_frame)
        vs_frame.pack()

        schedule_area = tk.Frame(vs_frame.interior)

        today = datetime.date.today()

        day_of_month = datetime.date.today().day
        first_day_date = today - datetime.timedelta(days=day_of_month - 1)

        monthrange = calendar.monthrange(today.year, today.month)
        first_day = monthrange[0]
        num_of_days = monthrange[1]

        date_list = [first_day_date + datetime.timedelta(days=day) for day in range(num_of_days)]

        row_num = 1
        column_num = first_day

        for num, date in enumerate(date_list):
            day_area = tk.LabelFrame(schedule_area, text=num + 1, width=150, height=150)
            day_area.grid(row=row_num, column=column_num, padx=2, pady=2, sticky='n')
            day_area.grid_columnconfigure(index=0, minsize=150, weight=1)
            day_area.grid_rowconfigure(index=0, minsize=150, weight=1)

            for item in self.database.database:
                if self.database.database[item].__dict__['date'] == date:
                    school_class = tk.LabelFrame(day_area, text='School class')
                    school_class.grid(row=0, column=0, sticky='we')
                    school_class.grid_columnconfigure(index=0, weight=1)
                    school_class.grid_rowconfigure(index=1, weight=1)

                    attrs = self.database.database[item].__dict__

                    for num2, attr in enumerate(attrs):
                        tk.Label(school_class,
                                 text=self.database.database[item].__dict__[attr]).grid(row=num2, column=0)

            edit_button = tk.Button(day_area, text='Edit',
                                    command=lambda date_=date: DayWindow(parent=self, database=self.database,
                                                                         date=date_))
            edit_button.place(x=115, y=-8)

            day_area.columnconfigure(0, weight=1)

            column_num += 1
            if column_num == 7:
                column_num = 0
                row_num += 1

        schedule_area.pack()


class DayWindow(tk.Toplevel):
    def __init__(self, parent=None, database=None, date=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent = parent
        self.database = database
        self.date = date
        self.label_names = ['Time', 'Classroom', 'Subject', 'Teacher', 'Type']
        self.entities = ['Classroom', 'Subject', 'Teacher']
        self.day_frames = []
        self.entries = []
        self.entity_id_dict = {}
        self.day_frame = None

        self.configure_widget()

    def configure_widget(self):
        from view.database import OptionMenuRelation

        self.day_frame = tk.Frame(self)
        self.day_frame.grid(row=0, column=0)

        last_row = 0
        for row, label_name in enumerate(self.label_names):
            tk.Label(self.day_frame, text=label_name).grid(row=row, column=0)

            entry = tk.Entry(self.day_frame)
            entry.grid(row=row, column=1)
            self.entries.append(entry)

            if label_name in self.entities:
                drop_down = OptionMenuRelation(parent=self.day_frame, folder='entity', entity=label_name.lower(),
                                               database=self.database, row=row, column=2)
                id_name_map = drop_down.id_name_map
                menu = drop_down.menu

                for option in id_name_map:
                    menu.add_command(label=id_name_map.get(option),
                                     command=lambda option_=option, value=id_name_map.get(option),
                                                    label_name_=label_name, entry_=entry:
                                     multi_functions(set_entry_text(entry_, value),
                                                     self.put_in_entity_id_dict(label_name_, option_)))
            last_row = row

        tk.Button(self.day_frame, text='OK', command=lambda: self.create_classes()).grid(row=last_row + 1, column=0)

    def put_in_entity_id_dict(self, label_name, option):
        self.entity_id_dict[label_name] = option

    def create_classes(self):
        self.database.open_database('entity', 'school_class')
        new_entity_id = self.database.biggest_id + 1

        time = self.day_frame.grid_slaves(row=0, column=1)[0].get()
        classroom = self.entity_id_dict.get('Classroom')
        subject = self.entity_id_dict.get('Subject')
        teacher = self.entity_id_dict.get('Teacher')
        type_ = self.day_frame.grid_slaves(row=4, column=1)[0].get()

        new_entity = SchoolClass(new_entity_id, self.date, time, classroom, subject, teacher, type_)

        self.database.database[new_entity_id] = new_entity
        self.database.save_database('entity', 'school_class')

        self.configure_widget()

        self.destroy()
