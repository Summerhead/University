import tkinter as tk
from os import listdir
from os.path import isfile, join

from db_model.database import Database
from entity.entity.building import Building
from entity.entity.classroom import Classroom
from entity.entity.college import College
from entity.entity.group import Group
from entity.entity.school_class import SchoolClass
from entity.entity.specialization import Specialization
from entity.entity.subject import Subject
from entity.entity.teacher import Teacher
from entity.relation_entity.college_specialization import CollegeSpecialization
from entity.relation_entity.specialization_subject import SpecializationSubject
from entity.relation_entity.teacher_subject import TeacherSubject

OPTIONS = ['Colleges', 'Specializations', 'Groups', 'Buildings', 'Classrooms', 'Subjects', 'Teachers']

OPTION_ENTITY_DICT = {'Colleges': College, 'Specializations': Specialization, 'Groups': Group,
                      'Buildings': Building, 'Classrooms': Classroom, 'Subjects': Subject, 'Teachers': Teacher,
                      'School_classes': SchoolClass}

FOREIGN_KEYS = ['College', 'Specialization', 'Building', 'Classroom', 'Subject', 'Teacher']

ENTITIES_CREATE_RELATION_MAP = {'Colleges': ['specialization'],
                                'Specializations': ['subject', 'college'],
                                'Teachers': ['subject'],
                                'Subjects': ['specialization', 'teacher']}

RELATION_ENTITY_FILE_NAMES = [f[:-3] for f in listdir('entity/relation_entity/') if
                              isfile(join('entity/relation_entity/', f))]


def multi_functions(*functions):
    def function(*args, **kwargs):
        for f in functions:
            f(*args, **kwargs)

    return function


def set_entry_text(entry, text):
    entry.delete(0, 'end')
    entry.insert(0, text)


class DatabaseFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.database = Database()
        self.table = None
        self.option_menu_var = None
        self.create_new_entity = None

        self.configure_widget()

    def configure_widget(self):
        from view.home import HomeFrame

        back = tk.Button(self, text='Back', command=lambda: self.master.switch_frame(HomeFrame))
        back.grid(row=0, column=0, padx=20, pady=20, ipadx=20)

        self.option_menu_var = tk.StringVar(self)

        drop_down = tk.OptionMenu(self, self.option_menu_var, ())
        drop_down.config(width=10)
        drop_down.grid(row=0, column=1, padx=20, pady=20, ipadx=20)

        menu = drop_down['menu']
        menu.delete(0, 'end')

        for option in OPTIONS:
            menu.add_command(label=option, command=lambda value=option: multi_functions(
                self.option_menu_var.set(value), self.database.open_database('entity', value[:-1].lower()),
                self.set_table(value)))

        self.option_menu_var.set('Choose table')

    def set_table(self, chosen_option):
        if self.table is not None:
            self.table.grid_forget()

        self.table = TableFrame(self, chosen_option, self.database)
        self.table.configure_widget()
        self.table.grid(row=1, column=1)

        if self.create_new_entity is not None:
            self.create_new_entity.grid_forget()

        self.create_new_entity = tk.Button(self, text='Create new',
                                           command=lambda: EntityWindow(self, chosen_option, self.database)
                                           .configure_widget())
        self.create_new_entity.grid(row=1, column=0)


class TableFrame(tk.Frame):
    def __init__(self, parent=None, chosen_option=None, database=None):
        super().__init__(parent)

        self.parent = parent
        self.chosen_option = chosen_option
        self.database = database

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.headers = []

    def configure_widget(self):
        self.configure_header()
        self.configure_table()

    def configure_header(self):
        for attribute in OPTION_ENTITY_DICT.get(self.chosen_option)().__dict__:
            fixed_attribute = attribute.replace('_', ' ').strip()
            fixed_attribute = fixed_attribute[0].upper() + fixed_attribute[1:]

            if attribute == '_id':
                fixed_attribute = fixed_attribute.upper()

            self.headers.append(fixed_attribute)

    def configure_table(self):
        frame = VerticalScrolledFrame(self)
        frame.grid(row=0, column=1, columnspan=len(self.headers), padx=10, pady=10)

        table_area = tk.Frame(frame.interior)

        for i, header in enumerate(self.headers):
            tk.Label(table_area, text=header).grid(row=0, column=i + 1, pady=2)

        db1 = self.database.database
        if db1 is not None and len(db1) > 0:
            for row_index, item in enumerate(db1):
                tk.Button(table_area, text='Edit',
                          command=lambda entity=db1[item]: multi_functions(
                              EntityWindow(self.parent, self.chosen_option, self.database, entity=entity)
                                  .configure_widget(fill=True))).grid(row=row_index + 1, column=0)

                attributes = db1[item].__dict__
                for column_index, attribute in enumerate(attributes):
                    if attribute[0].upper() + attribute[1:] in FOREIGN_KEYS:
                        self.database.open_database('entity', attribute)

                        db2 = self.database.database
                        for item2 in db2:
                            if db2[item2].__dict__['_id'] == attributes[attribute]:
                                tk.Label(table_area,
                                         text=db2[item2].__dict__['name']).grid(row=row_index + 1,
                                                                                column=column_index + 1)
                    else:
                        tk.Label(table_area,
                                 text=attributes[attribute]).grid(row=row_index + 1, column=column_index + 1)

        table_area.pack()


class EntityWindow(tk.Toplevel):
    def __init__(self, calling_frame=None, chosen_option=None, database=None, entity=None):
        super().__init__()

        self.calling_frame = calling_frame
        self.chosen_option = chosen_option
        self.database = database
        self.entity = entity
        self.main_frame = None
        self.relation_frame = None
        self.label_names = []
        self.entity_id_dict = {}
        self.new_entity_id = None
        self.change = None
        self.entries = []

    def configure_widget(self, fill=False):
        self.configure_content(fill=fill)

    def configure_main_frame(self):
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0)

        row = 0
        for attribute in OPTION_ENTITY_DICT.get(self.chosen_option)().__dict__:
            if attribute != '_id':
                label_name = attribute.replace('_', ' ').strip()
                label_name = label_name[0].upper() + label_name[1:]

                tk.Label(self.main_frame, text=label_name).grid(row=row, column=0)

                entry = tk.Entry(self.main_frame)
                entry.grid(row=row, column=1)
                self.entries.append(entry)

                if label_name in FOREIGN_KEYS:
                    drop_down = OptionMenuRelation(self.main_frame, 'entity', label_name.lower(), self.database,
                                                   row=row, column=2)

                    id_name_map = drop_down.id_name_map
                    menu = drop_down.menu

                    for option in id_name_map:
                        menu.add_command(label=id_name_map.get(option),
                                         command=lambda option_=option, value=id_name_map.get(option),
                                                        label_name_=label_name, entry_=entry: multi_functions(
                                             set_entry_text(entry_, value),
                                             self.put_in_entity_id_dict(label_name_, option_)))
                row = row + 1

        return row

    def configure_content(self, fill):
        last_row = self.configure_main_frame() + 1
        self.fill_frame_configure(fill)
        self.add_send_button(last_row)

        if self.chosen_option in ENTITIES_CREATE_RELATION_MAP:
            self.add_relation_frame()

    def fill_frame_configure(self, fill):
        if fill:
            self.fill_frame(self.entries, self.entity)
            self.new_entity_id = self.entity._id
            self.change = True
        else:
            self.new_entity_id = self.database.biggest_id
            self.change = False

    def add_send_button(self, row):
        tk.Button(self.main_frame, text='OK', command=lambda: multi_functions(
            self.create_new_entity(self.chosen_option, self.change))).grid(row=row + 1, column=0)

    def add_relation_frame(self):
        relatable_entities = ENTITIES_CREATE_RELATION_MAP.get(self.chosen_option)
        self.relation_frame = RelationFrame(self, self.entity, relatable_entities, self.database, self.chosen_option)
        self.relation_frame.configure_widget()
        self.relation_frame.grid(row=1, column=0)

    def put_in_entity_id_dict(self, label_name, option):
        self.entity_id_dict[label_name] = option

    def fill_frame(self, entries, entity):
        attributes = entity.__dict__
        needed_attributes = [attr for attr in attributes if attr != '_id' and attr != 'date']

        for entry, attribute in zip(entries, needed_attributes):
            if attribute[0].upper() + attribute[1:] in FOREIGN_KEYS:
                self.database.open_database('entity', attribute)

                for item in self.database.database:
                    if self.database.database[item].__dict__['_id'] == attributes[attribute]:
                        desired_attribute_name = 'name'

                        if attribute == 'classroom':
                            desired_attribute_name = 'number'

                        entry.insert(0, self.database.database[item].__dict__[desired_attribute_name])

            else:
                entry.insert(0, attributes[attribute])

    def create_new_entity(self, chosen_option, change):
        self.database.open_database('entity', chosen_option[:-1].lower())

        if not change:
            self.new_entity_id = self.database.biggest_id + 1

        new_entity = None

        if chosen_option == 'Colleges':
            name = self.main_frame.grid_slaves(row=0, column=1)[0].get()

            new_entity = College(_id=self.new_entity_id, name=name)

        if chosen_option == 'Specializations':
            name = self.main_frame.grid_slaves(row=0, column=1)[0].get()

            new_entity = Specialization(_id=self.new_entity_id, name=name)

        if chosen_option == 'Groups':
            number = self.main_frame.grid_slaves(row=0, column=1)[0].get()
            name = self.main_frame.grid_slaves(row=1, column=1)[0].get()
            specialization = self.entity_id_dict.get('Specialization')

            new_entity = Group(_id=self.new_entity_id, number=number, name=name, specialization=specialization)

        if chosen_option == 'Buildings':
            name = self.main_frame.grid_slaves(row=0, column=1)[0].get()
            address = self.main_frame.grid_slaves(row=1, column=1)[0].get()
            college = self.entity_id_dict.get('College')

            new_entity = Building(_id=self.new_entity_id, name=name, address=address, college=college)

        if chosen_option == 'Classrooms':
            number = self.main_frame.grid_slaves(row=0, column=1)[0].get()
            building = self.entity_id_dict.get('Building')

            new_entity = Classroom(_id=self.new_entity_id, number=number, building=building)

        if chosen_option == 'Subjects':
            name = self.main_frame.grid_slaves(row=0, column=1)[0].get()

            new_entity = Subject(_id=self.new_entity_id, name=name)

        if chosen_option == 'Teachers':
            name = self.main_frame.grid_slaves(row=0, column=1)[0].get()
            profession = self.main_frame.grid_slaves(row=1, column=1)[0].get()

            new_entity = Teacher(_id=self.new_entity_id, name=name, profession=profession)

        if chosen_option == 'School_class':
            time = self.main_frame.grid_slaves(row=0, column=1)[0].get()
            classroom = self.entity_id_dict.get('Classroom')
            subject = self.entity_id_dict.get('Subject')
            teacher = self.entity_id_dict.get('Teacher')
            type_ = self.main_frame.grid_slaves(row=4, column=1)[0].get()

            new_entity = SchoolClass(self.new_entity_id, self.date, time, classroom, subject, teacher, type_)


        else:
            Exception('Error in "create_new_entity". Unknown entity name: ' + chosen_option)

        if new_entity is None:
            Exception('New entity is None')

        self.database.database[self.new_entity_id] = new_entity

        self.database.save_database('entity', chosen_option[:-1].lower())
        self.database.update_biggest_id()

        self.calling_frame.set_table(chosen_option)

        if self.relation_frame is not None:
            self.relation_frame.entity = new_entity
            self.relation_frame.configure_widget()

            self.create_new_relation(self.new_entity_id, chosen_option)

    def create_new_relation(self, new_entity_id, chosen_option):
        relation_map = {chosen_option.lower()[:-1]: new_entity_id}

        entity_chosen_option_map = self.relation_frame.entity_chosen_option_map

        for item, file_name in zip(entity_chosen_option_map, self.relation_frame.file_names):
            self.database.open_database('relation_entity', file_name)

            for item2 in self.relation_frame.items_to_delete[file_name]:
                del self.database.database[item2]

            new_entity_id = self.database.biggest_id + 1
            for _id in entity_chosen_option_map.get(item):
                relation_map[item] = _id

                new_entity = None

                if file_name == 'college_specialization':
                    new_entity = CollegeSpecialization(new_entity_id, relation_map.get('college'),
                                                       relation_map.get('specialization'))
                if file_name == 'specialization_subject':
                    new_entity = SpecializationSubject(new_entity_id, relation_map.get('specialization'),
                                                       relation_map.get('subject'))
                if file_name == 'teacher_subject':
                    new_entity = TeacherSubject(new_entity_id, relation_map.get('teacher'),
                                                relation_map.get('subject'))
                else:
                    Exception('Error in "create_new_relation". Unknown file name: ' + file_name)

                self.database.database[new_entity_id] = new_entity
                new_entity_id += 1

            self.database.save_database('relation_entity', file_name)


class RelationFrame(tk.Frame):
    def __init__(self, parent, entity, relation_entities, database, chosen_option):
        super().__init__(parent)

        self.entity = entity
        self.relation_entities = relation_entities
        self.database = database
        self.chosen_option = chosen_option[:-1].lower()
        self.file_names = []
        self.chosen_options = {}
        self.entity_chosen_option_map = {}
        self.items_to_delete = {}

    def configure_widget(self):
        for column, relation_entity in enumerate(self.relation_entities):
            label = tk.Label(self, text='New ' + relation_entity + ' relation')
            label.grid(row=0, column=column)

            chosen_options = self.entity_chosen_option_map.get(relation_entity)

            if chosen_options is None:
                chosen_options = {}

            if self.entity is not None:
                self.filter_id_name_map(self.entity, relation_entity, chosen_options, column)

            self.entity_chosen_option_map[relation_entity] = chosen_options

            drop_down = OptionMenuRelation(self, 'entity', relation_entity, self.database, row=1, column=column,
                                           chosen_options=chosen_options)

            id_name_map = drop_down.id_name_map
            menu = drop_down.menu

            for option in id_name_map:
                menu.add_command(label=id_name_map.get(option),
                                 command=lambda _id=option, value=id_name_map.get(option), col=column,
                                                entity=relation_entity, dd=drop_down, lbl=label:
                                 multi_functions(
                                     self.create_new_relation(col, value),
                                     self.add_chosen_option(entity, dd, _id, value), lbl.grid_forget(),
                                     dd.grid_forget(), self.configure_widget()))

    def add_chosen_option(self, entity, drop_down, id, value):
        self.chosen_options = drop_down.chosen_options
        self.chosen_options[id] = value
        self.entity_chosen_option_map[entity] = self.chosen_options

    def create_new_relation(self, column, value):
        for slave in self.grid_slaves(column=column):
            if slave.grid_info()['row'] >= 2:
                label_text = slave.cget('text')

                label = tk.Label(self, text=label_text)
                label.grid(row=slave.grid_info()['row'] + 1, column=column)

                slave.grid_forget()

        tk.Label(self, text=value).grid(row=2, column=column)

    def filter_id_name_map(self, entity, relation_entity, chosen_options, column):
        for filename in RELATION_ENTITY_FILE_NAMES:
            if relation_entity in filename and self.chosen_option in filename:

                self.items_to_delete[filename] = []

                self.file_names.append(filename)
                self.database.open_database('relation_entity', filename)

                db1 = self.database.database

                if db1 is not None and len(db1) > 0:
                    row = 2

                    for item in db1:
                        id_chosen_option = db1[item].__dict__[self.chosen_option]
                        id_relatable_entity = db1[item].__dict__[relation_entity]

                        if id_chosen_option == entity._id:
                            self.items_to_delete[filename].append(item)

                            self.database.open_database('entity', relation_entity)
                            db2 = self.database.database

                            for item2 in db2:
                                attributes = self.database.database[item2].__dict__

                                if attributes['_id'] == id_relatable_entity:
                                    if attributes['_id'] not in chosen_options:
                                        tk.Label(self, text=attributes['name']).grid(row=row, column=column)
                                        row += 1

                                        chosen_options[attributes['_id']] = attributes['name']

                break


class OptionMenuRelation(tk.OptionMenu):
    def __init__(self, parent, folder, entity, database, row, column, chosen_options=None):
        self.parent = parent
        self.folder = folder
        self.entity = entity
        self.database = database
        self.row = row
        self.column = column
        if chosen_options is None:
            chosen_options = {}
        self.chosen_options = chosen_options

        self.option_menu_var = tk.StringVar(self.parent)

        super().__init__(self.parent, self.option_menu_var, ())

        self.grid(row=self.row, column=self.column)

        self.menu = self['menu']
        self.menu.delete(0, 'end')

        self.id_name_map = self.create_map(self.chosen_options.values())

    def create_map(self, chosen_options):
        self.database.open_database(self.folder, self.entity)

        self.parent.id_name_map = {}
        id_name_map = self.parent.id_name_map

        db1 = self.database.database
        if db1 is not None:
            if len(db1) > 0:
                for row_index, item in enumerate(db1):
                    attributes = db1[item].__dict__

                    if self.entity == 'classroom':
                        attr = 'number'
                    else:
                        attr = 'name'

                    if chosen_options is None or attributes[attr] not in chosen_options:
                        id_name_map[attributes['_id']] = attributes[attr]

                        if self.entity == 'building':
                            id_name_map[attributes['_id']] = \
                                f"{id_name_map[attributes['_id']]} ({attributes['address']})"

                        if self.entity == 'classroom':
                            self.database.open_database('entity', 'building')

                            db2 = self.database.database
                            for item2 in db2:
                                if item2 == attributes['building']:
                                    id_name_map[attributes['_id']] = \
                                        f"{id_name_map[attributes['_id']]}, {db2[item2].__dict__['name']} " \
                                        f"({db2[item2].__dict__['address']})"

        return id_name_map


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
