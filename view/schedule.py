import calendar
import datetime
import tkinter as tk

from entity.entity.school_class import SchoolClass
from view.database import set_entry_text, multi_functions, EntityWindow

BACKGROUND_COLORS = {'Лекция': 'white', 'Практика': '#ABF1FF', 'Зачет': '#EEFF97'}


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
        self.schedule_frame = None
        self.schedule_area = None
        self.database.open_database('entity', 'school_class')
        self.entities = ['Classroom', 'Subject', 'Teacher']
        self.today = datetime.date.today()
        self.date_list = None

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.configure_widget()

    def configure_widget(self):
        from view.home import HomeFrame

        if self is not None:
            self.grid_forget()

        back = tk.Button(self, text='Back', command=lambda: self.master.switch_frame(HomeFrame))
        back.grid(row=0, column=0, padx=20, pady=20, ipadx=20, sticky='n')

        self.schedule_frame = tk.LabelFrame(self, text='Schedule')
        self.schedule_frame.grid(row=0, column=1, padx=10, pady=10)
        self.schedule_frame.rowconfigure(1, weight=1)

        self.configure_headers()

        vs_frame = VerticalScrolledFrame(self.schedule_frame)
        vs_frame.pack()

        self.schedule_area = tk.Frame(vs_frame.interior)

        row = 0
        column = self.configure_dates()
        main_database = self.database.database

        self.configure_table(row, column, main_database)

    def configure_headers(self):
        day_names_area = tk.Frame(self.schedule_frame)

        day_names = calendar.day_name

        for num, day_name in enumerate(day_names):
            tk.Label(day_names_area, text=day_name).grid(row=0, column=num)
            day_names_area.grid_columnconfigure(num, weight=1, uniform='fred')

        day_names_area.pack(fill='x', expand=True, padx=(0, 20))

    def configure_dates(self):
        day_of_month = datetime.date.today().day
        first_day_date = self.today - datetime.timedelta(days=day_of_month - 1)

        monthrange = calendar.monthrange(self.today.year, self.today.month)
        first_day = monthrange[0]
        num_of_days = monthrange[1]

        self.date_list = [first_day_date + datetime.timedelta(days=day) for day in range(num_of_days)]

        return first_day

    def configure_table(self, day_area_row, day_area_column, main_database):
        for date_list_num, date in enumerate(self.date_list):
            day_area = tk.LabelFrame(self.schedule_area, text=date_list_num + 1, width=150, height=150)
            day_area.grid(row=day_area_row, column=day_area_column, padx=2, pady=2, sticky='n')
            day_area.grid_columnconfigure(index=0, minsize=150, weight=1)

            entities = []

            for item in main_database:
                attributes = main_database[item].__dict__

                if attributes['date'] == date:
                    entities.append(main_database[item])

                    bg = BACKGROUND_COLORS.get(attributes['type_'])

                    school_class = tk.LabelFrame(day_area, text=attributes['number'], bg=bg)
                    school_class.grid(row=int(attributes['number']) - 1, column=0, sticky='we')

                    for attributes_num, attribute_name in enumerate(attributes):
                        if attribute_name != '_id' and attribute_name != 'date' and attribute_name != 'number':
                            text = attributes[attribute_name]

                            if attribute_name[0].upper() + attribute_name[1:] in self.entities:
                                desired_attribute_name = 'name'

                                if attribute_name == 'classroom':
                                    desired_attribute_name = 'number'

                                self.database.open_database('entity', attribute_name)
                                related_database = self.database.database

                                for item2 in related_database:
                                    if related_database[item2].__dict__['_id'] == attributes[attribute_name]:
                                        text = related_database[item2].__dict__[desired_attribute_name]

                            tk.Label(school_class, text=text, wraplength=150,
                                     justify='left', bg=bg).grid(row=attributes_num, column=0, sticky='w')

            edit_button = tk.Button(day_area, text='Edit',
                                    command=lambda date_=date, entities_=entities: multi_functions(
                                        DayEntityWindow(calling_frame=self, database=self.database, date=date_,
                                                        entities=entities_).configure_widget()))
            edit_button.place(x=115, y=-8)

            day_area_column += 1
            if day_area_column == 7:
                day_area_column = 0
                day_area_row += 1

        self.schedule_area.pack()


# class DayWindow(tk.Toplevel):
#     def __init__(self, parent=None, database=None, date=None, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         self.parent = parent
#         self.database = database
#         self.date = date
#         self.label_names = ['Time', 'Classroom', 'Subject', 'Teacher', 'Type']
#         self.entities = ['Classroom', 'Subject', 'Teacher']
#         self.day_frames = []
#         self.entries = []
#         self.entity_id_dict = {}
#         self.day_frame = None
#
#         self.configure_widget()
#
#     def configure_widget(self):
#         from view.database import OptionMenuRelation
#
#         self.day_frame = tk.Frame(self)
#         self.day_frame.grid(row=0, column=0)
#
#         last_row = 0
#         for row, label_name in enumerate(self.label_names):
#             tk.Label(self.day_frame, text=label_name).grid(row=row, column=0)
#
#             entry = tk.Entry(self.day_frame)
#             entry.grid(row=row, column=1)
#             self.entries.append(entry)
#
#             if label_name in self.entities:
#                 drop_down = OptionMenuRelation(parent=self.day_frame, folder='entity', entity=label_name.lower(),
#                                                database=self.database, row=row, column=2)
#                 id_name_map = drop_down.id_name_map
#                 menu = drop_down.menu
#
#                 for option in id_name_map:
#                     menu.add_command(label=id_name_map.get(option),
#                                      command=lambda option_=option, value=id_name_map.get(option),
#                                                     label_name_=label_name, entry_=entry:
#                                      multi_functions(set_entry_text(entry_, value),
#                                                      self.put_in_entity_id_dict(label_name_, option_)))
#             last_row = row
#
#         tk.Button(self.day_frame, text='OK', command=lambda: self.create_classes()).grid(row=last_row + 1, column=0)
#
#     def put_in_entity_id_dict(self, label_name, option):
#         self.entity_id_dict[label_name] = option
#
#     def create_classes(self):
#         self.database.open_database('entity', 'school_class')
#         new_entity_id = self.database.biggest_id + 1
#
#         time = self.day_frame.grid_slaves(row=0, column=1)[0].get()
#         classroom = self.entity_id_dict.get('Classroom')
#         subject = self.entity_id_dict.get('Subject')
#         teacher = self.entity_id_dict.get('Teacher')
#         type_ = self.day_frame.grid_slaves(row=4, column=1)[0].get()
#
#         new_entity = SchoolClass(new_entity_id, self.date, time, classroom, subject, teacher, type_)
#
#         self.database.database[new_entity_id] = new_entity
#         self.database.save_database('entity', 'school_class')
#
#         self.parent.configure_widget()
#
#         self.destroy()

class DayEntityWindow(EntityWindow):
    def __init__(self, calling_frame=None, chosen_option='School_classes', database=None, entities=None, date=None):
        super().__init__(calling_frame=calling_frame, chosen_option=chosen_option, database=database, entities=entities)

        self.date = date
        self.day_frames = []
        self.entries = []
        self.entity_id_dict = {}
        self.day_frame = None
        self.number_of_entities = 0

    def configure_widget(self):
        super().configure_widget()
        self.add_new_class_button(self.main_frame.grid_size()[1])

    def add_new_class_button(self, row):
        # print(self.main_frame.grid_slaves(row=row - 1, column=0)[0])
        # for i in self.main_frame.grid_slaves():
        #     print(i.grid_info()['row'])
        ok_button = self.main_frame.grid_slaves(row=row - 1, column=0)[0]
        ok_button.grid(row=row, column=0)
        tk.Button(self.main_frame, text='Add class',
                  command=lambda: multi_functions(self.add_class_button_clicked(),
                                                  self.configure_main_frame(row=0, entities=self.number_of_entities),
                                                  self.fill_frame(),
                                                  self.database.open_database('entity', 'school_class'),
                                                  self.new_entity_id.append(
                                                      self.database.biggest_id + self.number_of_entities + 1),
                                                  ok_button.destroy(),
                                                  self.add_new_class_button(self.main_frame.grid_size()[1]))).grid(
            row=row - 1, column=0)

    def add_class_button_clicked(self):
        self.number_of_entities += 1
