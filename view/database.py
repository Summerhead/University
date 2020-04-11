import tkinter as tk
from os import listdir
from os.path import isfile, join

from db_model.database import Database
from entity.entity.building import Building
from entity.entity.college import College
from entity.entity.specialization import Specialization
from entity.entity.subject import Subject
from entity.entity.teacher import Teacher
from entity.relation_entity.college_specialization import CollegeSpecialization
from entity.relation_entity.specialization_subject import SpecializationSubject
from entity.relation_entity.specialization_teacher import SpecializationTeacher
from entity.relation_entity.teacher_subject import TeacherSubject


def multi_functions(*functions):
    def function(*args, **kwargs):
        for f in functions:
            f(*args, **kwargs)

    return function


def set_entry_text(entry, text):
    entry.delete(0, "end")
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

        options = ["Colleges", "Specializations", "Buildings", "Subjects", "Teachers"]

        menu = drop_down['menu']
        menu.delete(0, 'end')

        for option in options:
            menu.add_command(label=option, command=lambda value=option: multi_functions(
                self.option_menu_var.set(value), self.database.open_database(value),
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

        self.create_new_entity = tk.Button(self, text="Create new", command=lambda: NewEntityFrame(self)
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

        if option == 'Colleges':
            headers.append('ID')
            headers.append('Name')

        if option == 'Specializations':
            headers.append('ID')
            headers.append('Name')

        if option == 'Buildings':
            headers.append('ID')
            headers.append('Name')
            headers.append('Address')
            headers.append('College')

        if option == 'Subjects':
            headers.append('ID')
            headers.append('Name')

        if option == 'Teachers':
            headers.append('ID')
            headers.append('Name')
            headers.append('Address')
            headers.append('Profession')

        frame = VerticalScrolledFrame(self)
        frame.grid(row=0, column=1, columnspan=len(headers), padx=10, pady=10)

        table_area = tk.Frame(frame.interior)

        for i, header in enumerate(headers):
            tk.Label(table_area, text=header).grid(row=0, column=i + 1, pady=2)

        if database.database is not None and len(database.database) > 0:
            for row_index, item in enumerate(database.database):
                tk.Button(table_area, text="Edit",
                          command=lambda entity=database.database[item]: multi_functions(
                              NewEntityFrame(self.parent).configure_new_entity_frame(
                                  option, database, fill=True, entity=entity))).grid(row=row_index + 1, column=0)

                attributes = database.database[item].__dict__
                for column_index, attribute in enumerate(attributes):
                    tk.Label(table_area,
                             text=attributes[attribute]).grid(row=row_index + 1, column=column_index + 1)

        table_area.pack()


class NewEntityFrame(tk.Toplevel):
    def __init__(self, db_frame):
        super().__init__()

        self.db_frame = db_frame
        self.relation_frame = None

    def configure_new_entity_frame(self, chosen_option, database, fill=False, entity=None):
        labels = []

        foreign_keys = ["College"]

        entities_create_relation_map = {"Colleges": ["specializations"],
                                        "Specializations": ["subjects", "teachers", "colleges"],
                                        "Teachers": ["specializations", "subjects"],
                                        "Subjects": ["specializations", "teachers"]}

        if chosen_option == 'Colleges':
            labels.append('Name')

        if chosen_option == 'Specializations':
            labels.append('Name')

        if chosen_option == 'Buildings':
            labels.append('Name')
            labels.append('Address')
            labels.append('College')

        if chosen_option == 'Subjects':
            labels.append('Name')

        if chosen_option == 'Teachers':
            labels.append('Name')
            labels.append('Address')
            labels.append('Profession')

        last_row = 0
        entries = []
        for row, label in enumerate(labels):
            tk.Label(self, text=label).grid(row=row, column=0)

            entry = tk.Entry(self)
            entry.grid(row=row, column=1)

            entries.append(entry)

            if label in foreign_keys:
                drop_down = OptionMenuRelation(self, label + 's', database, row=row, column=2)

                id_name_map = drop_down.id_name_map
                menu = drop_down.menu

                for option in id_name_map:
                    menu.add_command(label=id_name_map.get(option),
                                     command=lambda value=id_name_map.get(option): multi_functions(
                                         set_entry_text(entry, value)))

                # tk.Button(self, text="Create new",
                #           command=lambda: self.parent(option)).grid(row=row, column=3)

            last_row = row

        if chosen_option in entities_create_relation_map:
            row = last_row + 1

            relatable_entities = entities_create_relation_map.get(chosen_option)

            self.relation_frame = RelationFrame(self, entity, relatable_entities, database, chosen_option)
            self.relation_frame.grid(row=row, column=0)

        database.open_database(chosen_option)

        if fill:
            self.fill_frame(entries, entity)
            new_entity_id = entity.id
            change = True
        else:
            new_entity_id = database.biggest_id
            change = False

        tk.Button(self, text="Send", command=lambda: multi_functions(self.create_new_entity(
            new_entity_id, chosen_option, change))).grid(row=0, column=2)

    def fill_frame(self, entries, entity):
        attributes = entity.__dict__
        needed_attributes = [attr for attr in attributes if attr != "id"]

        for entry, attribute in zip(entries, needed_attributes):
            entry.insert(0, attributes[attribute])

    def create_new_entity(self, new_entity_id, chosen_option, change):
        self.db_frame.database.open_database(chosen_option)

        if not change:
            new_entity_id = self.db_frame.database.biggest_id + 1

        new_entity = None

        if chosen_option == 'Colleges':
            name = self.grid_slaves(row=0, column=1)[0].get()

            new_entity = College(id=new_entity_id, name=name)

        if chosen_option == 'Specializations':
            name = self.grid_slaves(row=0, column=1)[0].get()

            new_entity = Specialization(id=new_entity_id, name=name)

        if chosen_option == 'Buildings':
            name = self.grid_slaves(row=0, column=1)[0].get()
            address = self.grid_slaves(row=1, column=1)[0].get()
            college = self.grid_slaves(row=2, column=1)[0].get()

            new_entity = Building(id=new_entity_id, name=name, address=address, college=college)

        if chosen_option == 'Subjects':
            name = self.grid_slaves(row=0, column=1)[0].get()

            new_entity = Subject(id=new_entity_id, name=name)

        if chosen_option == 'Teachers':
            name = self.grid_slaves(row=0, column=1)[0].get()
            address = self.grid_slaves(row=1, column=1)[0].get()
            profession = self.grid_slaves(row=2, column=1)[0].get()

            new_entity = Teacher(id=new_entity_id, name=name, address=address, profession=profession)

        else:
            Exception("Error in 'create_new_entity'. Unknown entity name: " + chosen_option)

        self.db_frame.database.database[new_entity_id] = new_entity

        self.db_frame.database.save_database(chosen_option)
        self.db_frame.database.update_biggest_id()

        self.db_frame.set_table(chosen_option)

        print("self.db_frame.database.database:", self.db_frame.database.database)
        if self.relation_frame is not None:
            print("self.relation_frame:", self.relation_frame)
            self.create_new_relation(new_entity_id, chosen_option)

        print("self.db_frame.database.database:", self.db_frame.database.database)
        #
        # print("self.db_frame.database.database:", self.db_frame.database.database)
        #
        # self.db_frame.database.open_database(chosen_option)
        # print("self.db_frame.database.database:", self.db_frame.database.database)

    def create_new_relation(self, new_entity_id, chosen_option):
        relation_map = {chosen_option.lower()[:-1]: new_entity_id}
        # print("relation_map:", relation_map)

        entity_chosen_option_map = self.relation_frame.entity_chosen_option_map
        # print("entity_chosen_option_map:", entity_chosen_option_map)

        for item, file_name in zip(entity_chosen_option_map, self.relation_frame.file_names):
            # print("item:", item)
            for id in entity_chosen_option_map.get(item):
                self.db_frame.database.open_database(file_name)

                new_entity_id = self.db_frame.database.biggest_id + 1
                # print("new_entity_id:", new_entity_id)

                relation_map[item[:-1]] = id

                new_entity = None
                if file_name == 'college_specialization':
                    new_entity = CollegeSpecialization(new_entity_id, relation_map.get('college'),
                                                       relation_map.get('specialization'))
                if file_name == 'specialization_subject':
                    new_entity = SpecializationSubject(new_entity_id, relation_map.get('specialization'),
                                                       relation_map.get('subject'))
                if file_name == 'specialization_teacher':
                    new_entity = SpecializationTeacher(new_entity_id, relation_map.get('specialization'),
                                                       relation_map.get('teacher'))
                if file_name == 'teacher_subject':
                    new_entity = TeacherSubject(new_entity_id, relation_map.get('teacher'),
                                                relation_map.get('subject'))
                else:
                    Exception("Error in 'create_new_relation'. Unknown file name: " + file_name)

                # print("new_entity:", new_entity)

                self.db_frame.database.database[new_entity_id] = new_entity

                self.db_frame.database.save_database(file_name)


class RelationFrame(tk.Frame):
    def __init__(self, parent, entity, relatable_entities, database, chosen_option):
        super().__init__(parent)

        self.entity = entity
        self.relatable_entities = relatable_entities
        self.database = database
        self.chosen_option = chosen_option
        self.file_names = []
        self.chosen_options = {}
        self.entity_chosen_option_map = {}

        self.configure_relation_frame()

    def configure_relation_frame(self):
        for column, relation_entity in enumerate(self.relatable_entities):
            label = tk.Label(self, text="New " + relation_entity[:-1] + " relation")
            label.grid(row=0, column=column)

            chosen_options = self.entity_chosen_option_map.get(relation_entity)

            if chosen_options is None:
                chosen_options = {}

            if self.entity is not None:
                print("self.entity_chosen_option_map:", self.entity_chosen_option_map)
                self.filter_id_name_map(self.entity, relation_entity, chosen_options, column)

            self.entity_chosen_option_map[relation_entity] = chosen_options
            print("self.entity_chosen_option_map:", self.entity_chosen_option_map)

            drop_down = OptionMenuRelation(self, relation_entity, self.database, row=1, column=column,
                                           chosen_options=chosen_options)

            id_name_map = drop_down.id_name_map
            print("id_name_map:", id_name_map)

            menu = drop_down.menu

            for option in id_name_map:
                menu.add_command(label=id_name_map.get(option),
                                 command=lambda _id=option, value=id_name_map.get(option), col=column,
                                                entity=relation_entity, dd=drop_down, lbl=label: multi_functions(
                                     self.create_new_relation(col, value),
                                     self.add_chosen_option(entity, dd, _id, value), lbl.grid_forget(),
                                     dd.grid_forget(), self.configure_relation_frame()))

    def add_chosen_option(self, entity, drop_down, id, value):
        self.chosen_options = drop_down.chosen_options
        self.chosen_options[id] = value
        self.entity_chosen_option_map[entity] = self.chosen_options
        # print("id:", id)
        # print("value:", value)
        print("self.chosen_options:", self.chosen_options)
        print("entity_chosen_option_map:", self.entity_chosen_option_map)

    def create_new_relation(self, column, value):
        print("value:", value)
        for slave in self.grid_slaves(column=column):
            if slave.grid_info()["row"] >= 2:
                # print("slave:", slave)
                # print("slave.grid_info()[row]:", slave.grid_info()["row"])
                label_text = slave.cget("text")
                print("label_text:", label_text)

                label = tk.Label(self, text=label_text)
                label.grid(row=slave.grid_info()["row"] + 1, column=column)
                print("row:", slave.grid_info()["row"] + 1)

                slave.grid_forget()

        tk.Label(self, text=value).grid(row=2, column=column)

    def filter_id_name_map(self, entity, relation_entity, chosen_options, column):
        onlyfiles = [f for f in listdir("entity/relation_entity/") if
                     isfile(join("entity/relation_entity/", f))]
        # print("entity.id:", entity.id)

        for filename in onlyfiles:
            if relation_entity[:-1] in filename and self.chosen_option.lower()[:-1] in filename:
                # print(f"relation_entity: {relation_entity}; chosen_option: {self.chosen_option}")
                # print("filename:", filename)

                self.file_names.append(filename[:-3])
                self.database.open_database(filename[:-3])

                if self.database.database is not None and len(self.database.database) > 0:
                    for item in self.database.database:
                        # print("self.database.database[item]:", self.database.database[item])
                        id_chosen_option = self.database.database[item].__dict__[self.chosen_option.lower()[:-1]]
                        id_relatable_entity = self.database.database[item].__dict__[relation_entity[:-1]]
                        # print("relation_entity:", relation_entity[:-1])
                        #
                        # print("self.chosen_option.lower()[:-1]:", self.chosen_option.lower()[:-1])
                        # print("id_chosen_option:", id_chosen_option)
                        # print("entity.id:", entity.id)
                        # print("id_relatable_entity:", id_relatable_entity)

                        if id_chosen_option == entity.id:
                            self.database.open_database(relation_entity)
                            # print("relation_entity:", relation_entity)

                            for item2 in self.database.database:
                                attributes = self.database.database[item2].__dict__

                                # print("attributes[id]:", attributes["id"])

                                if attributes["id"] == id_relatable_entity:
                                    # print(attributes["name"])

                                    if attributes["id"] not in chosen_options:
                                        tk.Label(self, text=attributes["name"]).grid(row=item2 + 1, column=column)
                                        
                                    print("attributes[name]:", attributes["name"])

                                    chosen_options[attributes["id"]] = attributes["name"]

                                    # del self.entity_chosen_option_map[relation_entity][attributes["id"]]
                                    # print("attributes[id];", attributes["id"])
                                    #
                                    # self.add_chosen_option(relation_entity, drop_down, attributes["id"],
                                    #                        attributes["name"])

                            self.database.open_database(filename[:-3])


class OptionMenuRelation(tk.OptionMenu):
    def __init__(self, parent, entity, database, row, column, chosen_options=None):
        self.parent = parent
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
        self.database.open_database(self.entity)

        self.parent.id_name_map = {}
        id_name_map = self.parent.id_name_map

        if self.database.database is not None:
            if len(self.database.database) > 0:
                for row_index, item in enumerate(self.database.database):
                    attributes = self.database.database[item].__dict__

                    if chosen_options is None or attributes['name'] not in chosen_options:
                        id_name_map[attributes['id']] = attributes['name']

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
