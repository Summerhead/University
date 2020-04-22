import calendar
import datetime
import tkinter as tk

from view.database import multi_functions, EntityWindow, set_entry_text, DatabaseFrame

TYPE_OPTIONS = ['Лекция', 'Практика', 'Зачет']

BACKGROUND_COLORS = {'Лекция': 'white', 'Практика': '#ABF1FF', 'Зачет': '#EEFF97'}

TIME = {1: '09:20', 2: '10:10', 3: '12:00', 4: '13:30', 5: '16:00', 6: '17:20', 7: '16:10'}


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
        from database.database import Database

        super().__init__(*args, **kwargs)

        self.database = Database()
        self.database.open_database('database/database_pickle/entity', 'school_class')
        self.schedule_frame = None
        self.schedule_area = None

        # db = self.database.database
        # for item in db:
        #     print('item,db[item]:', item, db[item])
        #     attrs = db[item].__dict__
        #     for attr in attrs:
        #         print('attr,attrs[attr]', attr, attrs[attr])

        self.entities = ['Classroom', 'Subject', 'Teacher']
        self.today = datetime.date.today()
        self.date_list = None

        self.rowconfigure(index=1, weight=1)
        self.columnconfigure(index=1, weight=1)

        self.configure_widget()

    def configure_widget(self):
        from view.home import HomeFrame

        if self is not None:
            self.grid_forget()

        back = tk.Button(self, text='Back', command=lambda: self.master.switch_frame(HomeFrame))
        back.grid(row=0, column=0, padx=20, pady=20, ipadx=20, sticky='n')

        back = tk.Button(self, text='Prev',
                         command=lambda: multi_functions(self.decrement_month(), self.configure_schedule()))
        back.grid(row=0, column=1, padx=20, pady=20, ipadx=20, sticky='n')

        back = tk.Button(self, text='Next',
                         command=lambda: multi_functions(self.increment_month(), self.configure_schedule()))
        back.grid(row=0, column=2, padx=20, pady=20, ipadx=20, sticky='n')

        self.configure_schedule()

    def configure_schedule(self):
        self.configure_schedule_frame()
        self.configure_headers()
        self.configure_schedule_area()
        self.configure_table()

    def configure_schedule_frame(self):
        if self.schedule_frame is not None:
            self.schedule_frame.destroy()
        self.schedule_frame = tk.LabelFrame(self, text='Schedule')
        self.schedule_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='n')
        self.schedule_frame.rowconfigure(index=1, weight=1)

    def configure_headers(self):
        day_names_area = tk.Frame(self.schedule_frame)
        day_names = calendar.day_name

        for num, day_name in enumerate(day_names):
            tk.Label(day_names_area, text=day_name).grid(row=0, column=num)
            day_names_area.grid_columnconfigure(num, weight=1, uniform='fred')

        day_names_area.pack(fill='x', expand=True, padx=(0, 20))

    def configure_schedule_area(self):
        vs_frame = VerticalScrolledFrame(self.schedule_frame)
        vs_frame.pack()

        self.schedule_area = tk.Frame(vs_frame.interior)

    def configure_dates(self):
        first_day_date = self.today.replace(day=1)

        monthrange = calendar.monthrange(self.today.year, self.today.month)
        first_day = monthrange[0]
        num_of_days = monthrange[1]

        self.date_list = [first_day_date + datetime.timedelta(days=day) for day in range(num_of_days)]

        return first_day

    def configure_table(self, option=None):
        day_area_row = 0
        day_area_column = self.configure_dates()

        main_database = self.database.database
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
                        if attribute_name != 'id_' and attribute_name != 'date':
                            text = attributes[attribute_name]

                            if attribute_name == 'number':
                                text = TIME.get(int(attributes[attribute_name]))

                            if attribute_name[0].upper() + attribute_name[1:] in self.entities:
                                desired_attribute_name = 'name'

                                if attribute_name == 'classroom':
                                    desired_attribute_name = 'number'

                                self.database.open_database('database/database_pickle/entity', attribute_name)
                                related_database = self.database.database

                                for item2 in related_database:
                                    if related_database[item2].__dict__['id_'] == attributes[attribute_name]:
                                        text = related_database[item2].__dict__[desired_attribute_name]

                            tk.Label(school_class, text=text, wraplength=150,
                                     justify='left', bg=bg).grid(row=attributes_num, column=0, sticky='w')

            tk.Button(day_area, text='Edit', command=lambda date_=date, entities_=entities: multi_functions(
                DayEntityWindow(calling_frame=self, database=self.database, date=date_,
                                entities=entities_).configure_widget())).place(x=115, y=-8)

            day_area_column += 1
            if day_area_column == 7:
                day_area_column = 0
                day_area_row += 1

        self.schedule_area.pack()

    def decrement_month(self):
        self.database.open_database('database/database_pickle/entity', 'school_class')
        self.today = self.today.replace(day=1) - datetime.timedelta(days=1)

    def increment_month(self):
        self.database.open_database('database/database_pickle/entity', 'school_class')
        monthrange = calendar.monthrange(self.today.year, self.today.month)
        num_of_days = monthrange[1]
        self.today = self.today.replace(day=num_of_days) + datetime.timedelta(days=1)


class DayEntityWindow(EntityWindow):
    def __init__(self, calling_frame=None, option='School classes', database=None, entities=None, date=None):
        super().__init__(calling_frame=calling_frame, option=option, database=database, entities=entities)

        self.date = date
        self.day_frames = []
        self.entries = []
        self.entity_id_dict = {}
        self.day_frame = None
        self.number_of_entities = len(entities) if len(entities) > 0 else 1
        self.num_classes = []

    def configure_widget(self):
        super().configure_widget()

        self.add_missing_widgets()
        self.add_new_class_button(self.main_frame.grid_size()[1] - 1)

    def add_missing_widgets(self):
        new_entity_id = self.new_entity_id
        new_entity_id.reverse()
        for num, (entity_frame, entity_id) in enumerate(zip(self.entities_frame.grid_slaves(), new_entity_id)):
            option_menu_var = tk.StringVar(entity_frame)
            drop_down = tk.OptionMenu(entity_frame, option_menu_var, ())
            drop_down.grid(row=0, column=2)

            menu = drop_down['menu']
            menu.delete(0, 'end')

            for num_class in range(1, 8):
                menu.add_command(label=num_class, command=lambda entity_frame_=entity_frame, num_class_=num_class:
                set_entry_text(entity_frame_.grid_slaves(row=0, column=1)[0], num_class_))

            option_menu_var = tk.StringVar(entity_frame)
            drop_down = tk.OptionMenu(entity_frame, option_menu_var, ())
            drop_down.grid(row=4, column=2)

            menu = drop_down['menu']
            menu.delete(0, 'end')

            for type_option in TYPE_OPTIONS:
                menu.add_command(label=type_option, command=lambda entity_frame_=entity_frame, type_option_=type_option:
                set_entry_text(entity_frame_.grid_slaves(row=4, column=1)[0], type_option_))

            tk.Button(entity_frame, text='Delete',
                      command=lambda entity_id_=entity_id: multi_functions(
                          DatabaseFrame().delete_entity(self.option, entity_id_), self.delete_from_entities(entity_id_),
                          self.configure_widget(),
                          self.database.open_database('database/database_pickle/entity', 'school_class'),
                          self.calling_frame.configure_schedule())).grid(row=0, rowspan=5, column=3)

    def add_new_class_button(self, row):
        ok_button = self.main_frame.grid_slaves(row=row, column=0)[0]
        ok_button.grid(row=row + 1, column=0)
        tk.Button(self.main_frame, text='Add class',
                  command=lambda: multi_functions(self.add_class_button_clicked(), self.change_to_true(),
                                                  self.configure_main_frame(row=0, entities=self.number_of_entities),
                                                  self.add_missing_widgets(),
                                                  self.fill_frame(), self.add_send_button(row=self.number_of_entities),
                                                  self.database.open_database('database/database_pickle/entity',
                                                                              'school_class'),
                                                  self.new_entity_id.append(
                                                      self.new_entity_id[len(self.new_entity_id) - 1] + 1),
                                                  ok_button.destroy(),
                                                  self.add_new_class_button(self.main_frame.grid_size()[1] - 1))).grid(
            row=row, column=0)

    def add_class_button_clicked(self):
        self.number_of_entities += 1

    def change_to_true(self):
        self.change = True

    def delete_from_entities(self, item):
        for num, entity_item in enumerate(self.entities):
            if entity_item.__dict__['id_'] == item:
                del self.entities[num]
                break
