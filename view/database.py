import tkinter as tk
from os import listdir
from os.path import isfile, join

from db_model.database import Database
from entity.entity.building import Building
from entity.entity.classroom import Classroom
from entity.entity.college import College
from entity.entity.group import Group
from entity.entity.specialization import Specialization
from entity.entity.subject import Subject
from entity.entity.teacher import Teacher
from entity.relation_entity.college_specialization import CollegeSpecialization
from entity.relation_entity.specialization_subject import SpecializationSubject
from entity.relation_entity.teacher_subject import TeacherSubject


def multi_functions(*functions):
    def function(*args, **kwargs):
        for f in functions:
            f(*args, **kwargs)

    return function


def set_entry_text(entry, text):
    entry.delete(0, 'end')
    entry.insert(0, text)


class DBFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        from view.home import HomeFrame

        self.database = Database()
        self.table = None
        self.create_new_entity = None

        back = tk.Button(self, text='Back', command=lambda: self.master.switch_frame(HomeFrame))
        back.grid(row=0, column=0, padx=20, pady=20, ipadx=20)

        self.option_menu_var = tk.StringVar(self)

        drop_down = tk.OptionMenu(self, self.option_menu_var, ())
        drop_down.config(width=10)
        drop_down.grid(row=0, column=1, padx=20, pady=20, ipadx=20)

        options = ['Colleges', 'Specializations', 'Groups', 'Buildings', 'Classrooms', 'Subjects', 'Teachers']

        menu = drop_down['menu']
        menu.delete(0, 'end')

        for option in options:
            menu.add_command(label=option, command=lambda value=option: multi_functions(
                self.option_menu_var.set(value), self.database.open_database('entity', value[:-1].lower()),
                self.set_table(value)))

        self.option_menu_var.set(options[0])

    def set_table(self, chosen_option):
        if self.table is not None:
            self.table.grid_forget()

        self.table = TableFrame(self)
        self.table.configure_table(chosen_option, self.database)
        self.table.grid(row=1, column=1)

        if self.create_new_entity is not None:
            self.create_new_entity.grid_forget()

        self.create_new_entity = tk.Button(self, text='Create new', command=lambda: NewEntityFrame(self)
                                           .configure_new_entity_frame(chosen_option, self.database))
        self.create_new_entity.grid(row=1, column=0)


class TableFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def configure_table(self, option, database):
        headers = []

        foreign_keys = ['College', 'Specialization', 'Building']

        if option == 'Colleges':
            headers.append('ID')
            headers.append('Name')

        if option == 'Specializations':
            headers.append('ID')
            headers.append('Name')

        if option == 'Groups':
            headers.append('ID')
            headers.append('Number')
            headers.append('Name')
            headers.append('Specialization')

        if option == 'Buildings':
            headers.append('ID')
            headers.append('Name')
            headers.append('Address')
            headers.append('College')

        if option == 'Classrooms':
            headers.append('ID')
            headers.append('Number')
            headers.append('Building')

        if option == 'Subjects':
            headers.append('ID')
            headers.append('Name')

        if option == 'Teachers':
            headers.append('ID')
            headers.append('Name')
            headers.append('Profession')

        frame = VerticalScrolledFrame(self)
        frame.grid(row=0, column=1, columnspan=len(headers), padx=10, pady=10)

        table_area = tk.Frame(frame.interior)

        for i, header in enumerate(headers):
            tk.Label(table_area, text=header).grid(row=0, column=i + 1, pady=2)

        db1 = database.database
        if db1 is not None and len(db1) > 0:
            for row_index, item in enumerate(db1):
                tk.Button(table_area, text='Edit',
                          command=lambda entity=db1[item]: multi_functions(
                              NewEntityFrame(self.parent).configure_new_entity_frame(
                                  option, database, fill=True, entity=entity))).grid(row=row_index + 1, column=0)

                attributes = db1[item].__dict__
                for column_index, attribute in enumerate(attributes):
                    print('attribute:', attribute)

                    if attribute[0].upper() + attribute[1:] in foreign_keys:
                        database.open_database('entity', attribute)

                        db2 = database.database
                        for item2 in db2:
                            if item2 == attributes[attribute]:
                                tk.Label(table_area,
                                         text=db2[item2].__dict__['name']).grid(row=row_index + 1,
                                                                                column=column_index + 1)
                    else:
                        tk.Label(table_area,
                                 text=attributes[attribute]).grid(row=row_index + 1, column=column_index + 1)

        table_area.pack()


class NewEntityFrame(tk.Toplevel):
    def __init__(self, db_frame):
        super().__init__()

        self.db_frame = db_frame
        self.relation_frame = None
        self.entity_id_dict = {}

    def configure_new_entity_frame(self, chosen_option, database, fill=False, entity=None):
        label_names = []

        foreign_keys = ['College', 'Specialization', 'Building', 'Classroom', 'Subject', 'Teacher']

        entities_create_relation_map = {'Colleges': ['specialization'],
                                        'Specializations': ['subject', 'college'],
                                        'Teachers': ['subject'],
                                        'Subjects': ['specialization', 'teacher']}

        if chosen_option == 'Colleges':
            label_names.append('Name')

        if chosen_option == 'Specializations':
            label_names.append('Name')

        if chosen_option == 'Groups':
            label_names.append('Number')
            label_names.append('Name')
            label_names.append('Specialization')

        if chosen_option == 'Buildings':
            label_names.append('Name')
            label_names.append('Address')
            label_names.append('College')

        if chosen_option == 'Classrooms':
            label_names.append('Number')
            label_names.append('Building')

        if chosen_option == 'Subjects':
            label_names.append('Name')

        if chosen_option == 'Teachers':
            label_names.append('Name')
            label_names.append('Profession')

        if chosen_option == 'Day':
            label_names = ['Time', 'Classroom', 'Subject', 'Teacher', 'Type']

        last_row = 0
        entries = []

        for row, label_name in enumerate(label_names):
            tk.Label(self, text=label_name).grid(row=row, column=0)

            entry = tk.Entry(self)
            entry.grid(row=row, column=1)

            entries.append(entry)

            if label_name in foreign_keys:
                drop_down = OptionMenuRelation(self, 'entity', label_name.lower(), database, row=row, column=2)

                id_name_map = drop_down.id_name_map
                menu = drop_down.menu

                for option in id_name_map:
                    menu.add_command(label=id_name_map.get(option),
                                     command=lambda option_=option, value=id_name_map.get(option),
                                                    label_name_=label_name: multi_functions(
                                         set_entry_text(entry, value),
                                         self.put_in_entity_id_dict(label_name_, option_)))

                # tk.Button(self, text='Create new',
                #           command=lambda: self.parent(option)).grid(row=row, column=3)

            last_row = row

        tk.Button(self, text='Send', command=lambda: multi_functions(self.create_new_entity(
            new_entity_id, chosen_option, change))).grid(row=last_row + 1, column=0)

        last_row = last_row + 1

        if chosen_option in entities_create_relation_map:
            relatable_entities = entities_create_relation_map.get(chosen_option)

            self.relation_frame = RelationFrame(self, entity, relatable_entities, database, chosen_option)
            self.relation_frame.grid(row=last_row + 1, column=0)

        # database.open_database('entity', chosen_option[:-1].lower())

        if fill:
            self.fill_frame(entries, entity)
            new_entity_id = entity._id
            change = True
        else:
            new_entity_id = database.biggest_id
            change = False

    def put_in_entity_id_dict(self, label_name, option):
        self.entity_id_dict[label_name] = option

    def fill_frame(self, entries, entity):
        foreign_keys = ['College', 'Specialization', 'Building']

        attributes = entity.__dict__
        needed_attributes = [attr for attr in attributes if attr != '_id']

        for entry, attribute in zip(entries, needed_attributes):
            if attribute[0].upper() + attribute[1:] in foreign_keys:
                self.db_frame.database.open_database('entity', attribute)

                for item in self.db_frame.database.database:
                    if item == attributes[attribute]:
                        entry.insert(0, self.db_frame.database.database[item].__dict__['name'])

            else:
                entry.insert(0, attributes[attribute])

    def create_new_entity(self, new_entity_id, chosen_option, change):
        self.db_frame.database.open_database('entity', chosen_option[:-1].lower())

        if not change:
            new_entity_id = self.db_frame.database.biggest_id + 1

        new_entity = None

        if chosen_option == 'Colleges':
            name = self.grid_slaves(row=0, column=1)[0].get()

            new_entity = College(_id=new_entity_id, name=name)

        if chosen_option == 'Specializations':
            name = self.grid_slaves(row=0, column=1)[0].get()

            new_entity = Specialization(_id=new_entity_id, name=name)

        if chosen_option == 'Groups':
            number = self.grid_slaves(row=0, column=1)[0].get()
            name = self.grid_slaves(row=1, column=1)[0].get()
            specialization = self.entity_id_dict.get('Specialization')

            new_entity = Group(_id=new_entity_id, number=number, name=name, specialization=specialization)

        if chosen_option == 'Buildings':
            name = self.grid_slaves(row=0, column=1)[0].get()
            address = self.grid_slaves(row=1, column=1)[0].get()
            college = self.entity_id_dict.get('College')

            new_entity = Building(_id=new_entity_id, name=name, address=address, college=college)

        if chosen_option == 'Classrooms':
            number = self.grid_slaves(row=0, column=1)[0].get()
            building = self.entity_id_dict.get('Building')

            new_entity = Classroom(_id=new_entity_id, number=number, building=building)

        if chosen_option == 'Subjects':
            name = self.grid_slaves(row=0, column=1)[0].get()

            new_entity = Subject(_id=new_entity_id, name=name)

        if chosen_option == 'Teachers':
            name = self.grid_slaves(row=0, column=1)[0].get()
            profession = self.grid_slaves(row=1, column=1)[0].get()

            new_entity = Teacher(_id=new_entity_id, name=name, profession=profession)

        else:
            Exception('Error in "create_new_entity". Unknown entity name: ' + chosen_option)

        self.db_frame.database.database[new_entity_id] = new_entity

        self.db_frame.database.save_database('entity', chosen_option[:-1].lower())
        self.db_frame.database.update_biggest_id()

        self.db_frame.set_table(chosen_option)

        if self.relation_frame is not None:
            self.relation_frame.entity = new_entity
            self.relation_frame.configure_relation_frame()

            self.create_new_relation(new_entity_id, chosen_option)

    def create_new_relation(self, new_entity_id, chosen_option):
        relation_map = {chosen_option.lower()[:-1]: new_entity_id}

        entity_chosen_option_map = self.relation_frame.entity_chosen_option_map

        for item, file_name in zip(entity_chosen_option_map, self.relation_frame.file_names):
            self.db_frame.database.open_database('relation_entity', file_name)

            for item2 in self.relation_frame.items_to_delete[file_name]:
                del self.db_frame.database.database[item2]

            new_entity_id = self.db_frame.database.biggest_id + 1
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

                self.db_frame.database.database[new_entity_id] = new_entity
                new_entity_id += 1

            self.db_frame.database.save_database('relation_entity', file_name)


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

        self.configure_relation_frame()

    def configure_relation_frame(self):
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
                                     dd.grid_forget(), self.configure_relation_frame()))

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
        onlyfiles = [f[:-3] for f in listdir('entity/relation_entity/') if
                     isfile(join('entity/relation_entity/', f))]

        for filename in onlyfiles:
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
