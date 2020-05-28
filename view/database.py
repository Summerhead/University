import tkinter as tk
from os import listdir
from os.path import isfile, join

from database.database import Database
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

OPTIONS = ['Colleges', 'Specializations', 'Groups', 'Buildings', 'Classrooms', 'Subjects', 'Teachers', 'ColSpec',
           'SpecSub', 'TeachSub']

OPTION_ENTITY_FILEPATH_DICT = {'Colleges': {'entity_name': College,
                                            'filepath': {'folder': 'database/database_pickle/entity',
                                                         'file_name': 'college'}},
                               'Specializations': {'entity_name': Specialization,
                                                   'filepath': {'folder': 'database/database_pickle/entity',
                                                                'file_name': 'specialization'}},
                               'Groups': {'entity_name': Group,
                                          'filepath': {'folder': 'database/database_pickle/entity',
                                                       'file_name': 'group'}},
                               'Buildings': {'entity_name': Building,
                                             'filepath': {'folder': 'database/database_pickle/entity',
                                                          'file_name': 'building'}},
                               'Classrooms': {'entity_name': Classroom,
                                              'filepath': {'folder': 'database/database_pickle/entity',
                                                           'file_name': 'classroom'}},
                               'Subjects': {'entity_name': Subject,
                                            'filepath': {'folder': 'database/database_pickle/entity',
                                                         'file_name': 'subject'}},
                               'Teachers': {'entity_name': Teacher,
                                            'filepath': {'folder': 'database/database_pickle/entity',
                                                         'file_name': 'teacher'}},
                               'School classes': {'entity_name': SchoolClass,
                                                  'filepath': {'folder': 'database/database_pickle/entity',
                                                               'file_name': 'school_class'}},
                               'ColSpec': {'entity_name': CollegeSpecialization,
                                           'filepath': {'folder': 'database/database_pickle/relation_entity',
                                                        'file_name': 'college_specialization'}},
                               'SpecSub': {'entity_name': SpecializationSubject,
                                           'filepath': {'folder': 'database/database_pickle/relation_entity',
                                                        'file_name': 'specialization_subject'}},
                               'TeachSub': {'entity_name': TeacherSubject,
                                            'filepath': {'folder': 'database/database_pickle/relation_entity',
                                                         'file_name': 'teacher_subject'}},
                               'Test': {'entity_name': Subject,
                                        'filepath': {
                                            'folder': 'C:/Users/Dreampopper/safu/3 курс 2 семестр/ооп/проект/tests',
                                            'file_name': 'test_subject'}}}

FILENAME_FOLDER_DICT = {'college': 'database/database_pickle/entity',
                        'specialization': 'database/database_pickle/entity', 'group': 'database/database_pickle/entity',
                        'building': 'database/database_pickle/entity', 'classroom': 'database/database_pickle/entity',
                        'subject': 'database/database_pickle/entity', 'teacher': 'database/database_pickle/entity',
                        'school_class': 'database/database_pickle/entity',
                        'college_specialization': 'database/database_pickle/relation_entity',
                        'specialization_subject': 'database/database_pickle/relation_entity',
                        'teacher_subject': 'database/database_pickle/relation_entity',
                        'test_subject': 'C:/Users/Dreampopper/safu/3 курс 2 семестр/ооп/проект/tests'}

FOREIGN_KEYS = ['college', 'specialization', 'building', 'classroom', 'subject', 'teacher']

ENTITIES_CREATE_RELATION_DICT = {'Colleges': ['specialization'],
                                 'Specializations': ['subject', 'college'],
                                 'Teachers': ['subject'],
                                 'Subjects': ['specialization', 'teacher']}

RELATION_ENTITY_FILE_NAMES = \
    [file_name.replace('.py', '') for file_name in
     listdir('C:/Users/Dreampopper/safu/3 курс 2 семестр/ооп/проект/entity/relation_entity/') if
     isfile(join('C:/Users/Dreampopper/safu/3 курс 2 семестр/ооп/проект/entity/relation_entity/', file_name))
     and file_name != '__init__.py']


def multi_functions(*functions):
    def function(*args, **kwargs):
        for f in functions:
            f(*args, **kwargs)

    return function


def set_entry_text(entry, text):
    entry.delete(0, 'end')
    entry.insert(0, text)


class DatabaseFrame(tk.Frame):
    """
    Панель окна базы данных.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.database = Database()
        self.table = None
        self.option_menu_var = None
        self.create_new_entity = None
        self.option_bar = None
        self.rowconfigure(index=1, weight=1)
        self.columnconfigure(index=1, weight=1)

        self.configure_widget()

    def configure_widget(self):
        """
        Конфигурирует панель окна базы данных.
        :return:
        """
        from view.home import HomeFrame

        self.option_bar = tk.Frame(self)
        self.option_bar.grid(row=0, column=0)

        back = tk.Button(self.option_bar, text='Back', command=lambda: self.master.switch_frame(HomeFrame))
        back.grid(row=0, column=0, padx=20, pady=20, ipadx=20)

        self.option_menu_var = tk.StringVar(self)

        drop_down = tk.OptionMenu(self.option_bar, self.option_menu_var, ())
        drop_down.config(width=10)
        drop_down.grid(row=0, column=1, padx=20, pady=20, ipadx=20, sticky='w')

        menu = drop_down['menu']
        menu.delete(0, 'end')

        for option in OPTIONS:
            menu.add_command(label=option, command=lambda option_=option: multi_functions(
                self.option_menu_var.set(option_), self.configure_table(option_)))

        self.option_menu_var.set('Choose table')

    def configure_table(self, option):
        """
        Конфигурирует таблицу.
        :param option:
        :return:
        """
        if self.table is not None:
            self.table.grid_forget()

        self.database.open_database(OPTION_ENTITY_FILEPATH_DICT.get(option)['filepath']['folder'],
                                    OPTION_ENTITY_FILEPATH_DICT.get(option)['filepath']['file_name'])
        self.table = TableFrame(self, option, self.database)
        self.table.configure_widget()
        self.table.grid(row=1, column=0, columnspan=3, sticky='n')
        self.table.rowconfigure(index=1, weight=1)

        if self.create_new_entity is not None:
            self.create_new_entity.grid_forget()

        self.create_new_entity = tk.Button(self.option_bar, text='Create new',
                                           command=lambda: EntityWindow(self, option, self.database)
                                           .configure_widget())
        self.create_new_entity.grid(row=0, column=2, sticky='w')

    def delete_entity(self, option, item):
        """
        Удаляет сущность из базы банных.
        :param option:
        :param item:
        :return:
        """
        file_name = OPTION_ENTITY_FILEPATH_DICT.get(option)['filepath']['file_name']

        self.database.open_database(OPTION_ENTITY_FILEPATH_DICT.get(option)['filepath']['folder'], file_name)
        del self.database.database[item]
        self.database.save_database(FILENAME_FOLDER_DICT.get(file_name), file_name)

        for relation_entity_file_name in RELATION_ENTITY_FILE_NAMES:
            items_to_delete = []
            if file_name in relation_entity_file_name:
                self.database.open_database(
                    FILENAME_FOLDER_DICT.get(relation_entity_file_name),
                    relation_entity_file_name)

                db = self.database.database
                for item2 in db:
                    if item == self.database.database[item2].__dict__[file_name]:
                        items_to_delete.append(item2)

                for item2 in items_to_delete:
                    del db[item2]

                self.database.save_database(FILENAME_FOLDER_DICT.get(relation_entity_file_name),
                                            relation_entity_file_name)


class TableFrame(tk.Frame):
    """
    Панель таблицы.
    """

    def __init__(self, parent=None, option=None, database=None):
        super().__init__(parent)

        self.parent = parent
        self.option = option
        self.file_name = OPTION_ENTITY_FILEPATH_DICT.get(self.option)['filepath']['file_name']
        self.database = database
        self.headers = []

    def configure_widget(self):
        self.configure_header()
        self.configure_table()

    def configure_header(self):
        """
        Конфигурирует заголовки таблицы.
        :return:
        """
        for attribute in OPTION_ENTITY_FILEPATH_DICT.get(self.option)['entity_name']().__dict__:
            fixed_attribute = attribute.replace('_', ' ').strip()
            fixed_attribute = fixed_attribute[0].upper() + fixed_attribute[1:]

            if attribute == 'id_':
                fixed_attribute = fixed_attribute.upper()

            self.headers.append(fixed_attribute)

    def configure_table(self):
        """
        Конфигурирует тело таблицы.
        :return:
        """
        from view.schedule import VerticalScrolledFrame

        frame = VerticalScrolledFrame(self)
        frame.grid(row=0, column=1, columnspan=len(self.headers), padx=10, pady=10)

        table_area = tk.Frame(frame.interior)

        for i, header in enumerate(self.headers):
            tk.Label(table_area, text=header).grid(row=0, column=i + 2, pady=2)

        db1 = self.database.database
        if db1 is not None and len(db1) > 0:
            for row_index, item in enumerate(db1):
                tk.Button(table_area, text='Delete', command=lambda item_=item: multi_functions(
                    WarningWindow(self.parent, self.option, item_)
                        .configure_widget())).grid(row=row_index + 1, column=0)

                tk.Button(table_area, text='Edit', command=lambda entity=db1[item]: multi_functions(
                    EntityWindow(self.parent, self.option, self.database, entities=[entity])
                        .configure_widget())).grid(row=row_index + 1, column=1)

                attributes = db1[item].__dict__
                for column_index, attribute in enumerate(attributes):
                    if attribute in FOREIGN_KEYS:
                        self.database.open_database(FILENAME_FOLDER_DICT.get(attribute), attribute)

                        db2 = self.database.database
                        for item2 in db2:
                            if db2[item2].__dict__['id_'] == attributes[attribute]:
                                tk.Label(table_area,
                                         text=db2[item2].__dict__['name']).grid(row=row_index + 1,
                                                                                column=column_index + 2)
                    else:
                        tk.Label(table_area,
                                 text=attributes[attribute]).grid(row=row_index + 1, column=column_index + 2)

        table_area.pack()


class WarningWindow(tk.Toplevel):
    """
    Окно, предупреждающее об удалении сущности из базы данных.
    """

    def __init__(self, parent, option, item):
        super().__init__()

        self.parent = parent
        self.option = option
        self.item = item

    def configure_widget(self):
        """
        Конфигурация окна предупреждения.
        :return:
        """
        tk.Label(self, text='Are you sure you want to delete this entity?').grid(row=0, column=0, columnspan=2, padx=10,
                                                                                 pady=10)
        tk.Button(self, text='No', command=lambda: self.destroy()).grid(row=1, column=0, padx=10, pady=10, sticky='e')
        tk.Button(self, text='Yes', command=lambda: multi_functions(
            self.parent.delete_entity(self.option, self.item), self.parent.configure_table(self.option),
            self.destroy())).grid(row=1, column=1, padx=10, pady=10, sticky='w')


class EntityWindow(tk.Toplevel):
    """
    Окно сущности.
    """

    def __init__(self, calling_frame=None, option=None, database=None, entities=None):
        super().__init__()

        self.calling_frame = calling_frame
        self.option = option
        self.database = database
        if entities is None:
            entities = []
        self.entities = entities
        self.main_frame = None
        self.entities_frame = None
        self.relation_frame = None
        self.label_names = []
        self.entity_id_dict = {}
        self.new_entity_id = []
        self.change = None
        self.entries = []
        self.attribute_list = []

    def configure_widget(self):
        """
        Конфигурация окна сущности.
        :return:
        """
        self.columnconfigure(index=0, weight=1)
        self.configure_content()

    def configure_content(self):
        """
        Конфигурация контента окна сущности.
        :return:
        """
        entities = len(self.entities)
        if entities == 0:
            entities = 1
        last_row = self.configure_main_frame(row=0, entities=entities)

        self.fill_frame_configure()
        self.add_send_button(last_row + 1)

        if self.option in ENTITIES_CREATE_RELATION_DICT:
            self.add_relation_frame()

    def configure_main_frame(self, row, entities):
        """
        Конфигурация основной панели окна сущности.
        :param row:
        :param entities:
        :return:
        """
        if self.main_frame is not None:
            self.main_frame.destroy()

        if self.entities_frame is not None:
            self.entities_frame.destroy()

        if self.relation_frame is not None:
            self.relation_frame.destroy()

        if len(self.entries) > 0:
            self.entries = []

        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0)

        self.entities_frame = tk.Frame(self.main_frame)
        self.entities_frame.grid(row=0, column=0)

        for entity_row in range(entities):
            entity_frame = tk.LabelFrame(self.entities_frame)
            entity_frame.grid(row=entity_row, column=0, pady=10)

            entity_entries = []
            self.attribute_list = []

            attribute_row = 0
            for attribute in OPTION_ENTITY_FILEPATH_DICT.get(self.option)['entity_name']().__dict__:
                if attribute != 'id_' and attribute != 'date':
                    label_name = attribute.replace('_', ' ').strip()
                    label_name = label_name[0].upper() + label_name[1:]

                    tk.Label(entity_frame, text=label_name).grid(row=attribute_row, column=0)

                    entry = tk.Entry(entity_frame)
                    entry.grid(row=attribute_row, column=1)

                    entity_entries.append(entry)

                    self.attribute_list.append(attribute)

                    if attribute in FOREIGN_KEYS:
                        drop_down = RelationOptionMenu(entity_frame, 'entity', attribute, self.database,
                                                       row=attribute_row, column=2)
                        id_name_map = drop_down.id_name_map
                        menu = drop_down.menu

                        for option in id_name_map:
                            menu.add_command(label=id_name_map.get(option),
                                             command=lambda option_=option, value=id_name_map.get(option),
                                                            label_name_=label_name, entry_=entry: multi_functions(
                                                 set_entry_text(entry_, value),
                                                 self.put_in_entity_id_dict(entry_, option_)))
                    attribute_row += 1

            self.entries.append(entity_entries)
            row = entity_row

        self.database.open_database(OPTION_ENTITY_FILEPATH_DICT.get(self.option)['filepath']['folder'],
                                    OPTION_ENTITY_FILEPATH_DICT.get(self.option)['filepath']['file_name'])

        return row

    def fill_frame_configure(self):
        """
        Метод, определяющий, необходимо ли внести изменения в существующую сущность или создать новую.
        :return:
        """
        if len(self.entities) > 0:
            self.fill_frame()
            self.new_entity_id = [entity.id_ for entity in self.entities]
            self.change = True
        else:
            self.new_entity_id = [self.database.biggest_id + 1]
            self.change = False

    def add_send_button(self, row):
        """
        Добавляет кнопку подтверждения действия в окне сущности.
        :param row:
        :return:
        """
        send_buttons_frame = tk.Frame(self.main_frame)
        send_buttons_frame.grid(row=row, column=0)

        tk.Button(send_buttons_frame, text='Save & Next', command=lambda: multi_functions(
            self.create_new_entity(self.option, self.change), self.clear_entities(),
            self.configure_next_entity_frame())).grid(row=row, column=0)

        tk.Button(send_buttons_frame, text='Save & Close', command=lambda: multi_functions(
            self.create_new_entity(self.option, self.change), self.destroy())).grid(row=row, column=1)

    def clear_entities(self):
        """
        Очищает стек сущностей.
        :return:
        """
        self.entities = []

    def add_relation_frame(self):
        """
        Добавляет панель связанных сущностей.
        :return:
        """
        relatable_entities = ENTITIES_CREATE_RELATION_DICT.get(self.option)
        self.relation_frame = RelationFrame(self, self.entities, relatable_entities, self.database, self.option)
        self.relation_frame.configure_widget()
        self.relation_frame.grid(row=1, column=0)

    def put_in_entity_id_dict(self, entry, option):
        """
        Помещает пару "поле ввода-id опции" в словарь.
        :param entry:
        :param option:
        :return:
        """
        self.entity_id_dict[entry] = option

    def fill_frame(self):
        """
        Заполняет панель сущности соответствующими данными этой сущности из базы данных.
        :return:
        """
        for entity_entries, entity in zip(self.entries, self.entities):
            attributes = entity.__dict__
            needed_attributes = [attr for attr in attributes if attr != 'id_' and attr != 'date']

            for entry, attribute in zip(entity_entries, needed_attributes):
                if attribute in FOREIGN_KEYS:
                    self.database.open_database(FILENAME_FOLDER_DICT.get(attribute), attribute)

                    relatable_entity_database = self.database.database
                    for item in relatable_entity_database:
                        if relatable_entity_database[item].__dict__['id_'] == attributes[attribute]:
                            desired_attribute_name = 'name'

                            if attribute == 'classroom':
                                desired_attribute_name = 'number'

                            entry.insert(0, relatable_entity_database[item].__dict__[desired_attribute_name])
                            self.put_in_entity_id_dict(entry, relatable_entity_database[item].__dict__['id_'])

                else:
                    entry.insert(0, attributes[attribute])

    def create_new_entity(self, option, change):
        """
        Создает новую сущность и записывает в базу данных.
        :param option:
        :param change:
        :return:
        """
        self.database.open_database(OPTION_ENTITY_FILEPATH_DICT.get(option)['filepath']['folder'],
                                    OPTION_ENTITY_FILEPATH_DICT.get(option)['filepath']['file_name'])

        if not change:
            self.new_entity_id = [self.database.biggest_id + 1]
        else:
            self.entities = []

        new_entity = None

        for num, entity_frame in enumerate(self.entities_frame.grid_slaves()):
            kwargs = {}
            for attribute, entry in zip(self.attribute_list, self.entries[num]):
                if entry in self.entity_id_dict:
                    attribute_value = self.entity_id_dict[entry]
                else:
                    attribute_value = entry.get()
                kwargs[attribute] = attribute_value

            if option == 'School classes':
                kwargs['date'] = self.date

            new_entity = OPTION_ENTITY_FILEPATH_DICT.get(option)['entity_name'](id_=self.new_entity_id[num - 1],
                                                                                **kwargs)

            if change:
                self.entities.append(new_entity)

            if new_entity is None:
                Exception('New entity is None')

            self.database.database[self.new_entity_id[num - 1]] = new_entity
            self.database.save_database(OPTION_ENTITY_FILEPATH_DICT.get(option)['filepath']['folder'],
                                        OPTION_ENTITY_FILEPATH_DICT.get(option)['filepath']['file_name'])

        if self.relation_frame is not None:
            self.relation_frame.entities = [new_entity]
            self.relation_frame.configure_widget()
            self.create_new_relation(self.new_entity_id[0], option)

        self.calling_frame.configure_table(option)

    def configure_next_entity_frame(self):
        """
        Конфигурирует новую панель для следующей сущности.
        :return:
        """
        self.configure_widget()

    def create_new_relation(self, new_entity_id, chosen_option):
        """
        Создает новую связь и записывает в базу данных.
        :param new_entity_id:
        :param chosen_option:
        :return:
        """
        relation_map = {OPTION_ENTITY_FILEPATH_DICT.get(chosen_option)['filepath']['file_name']: new_entity_id}

        entity_chosen_option_map = self.relation_frame.entity_chosen_option_map

        for item, file_name in zip(entity_chosen_option_map, self.relation_frame.file_names):
            self.database.open_database(FILENAME_FOLDER_DICT.get(file_name), file_name)

            for item2 in self.relation_frame.items_to_delete[file_name]:
                del self.database.database[item2]

            new_entity_id = self.database.biggest_id + 1
            for id_ in entity_chosen_option_map.get(item):
                relation_map[item] = id_

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

            self.database.save_database(FILENAME_FOLDER_DICT.get(file_name), file_name)


class RelationFrame(tk.Frame):
    """
    Панель связанных сущностей.
    """

    def __init__(self, parent, entities, relation_entities, database, chosen_option):
        super().__init__(parent)

        self.entities = entities
        self.relation_entities = relation_entities
        self.database = database
        self.chosen_option = OPTION_ENTITY_FILEPATH_DICT.get(chosen_option)['filepath']['file_name']
        self.file_names = []
        self.chosen_options = {}
        self.entity_chosen_option_map = {}
        self.items_to_delete = {}

    def configure_widget(self):
        """
        Конфигурирует панель связанных сущностей.
        :return:
        """
        for column, relation_entity in enumerate(self.relation_entities):
            label = tk.Label(self, text='New ' + relation_entity + ' relation')
            label.grid(row=0, column=column)

            chosen_options = self.entity_chosen_option_map.get(relation_entity)

            if chosen_options is None:
                chosen_options = {}

            if len(self.entities) > 0:
                self.filter_id_name_map(self.entities[0], relation_entity, chosen_options, column)

            self.entity_chosen_option_map[relation_entity] = chosen_options

            drop_down = RelationOptionMenu(self, 'entity', relation_entity, self.database, row=1, column=column,
                                           chosen_options=chosen_options)
            id_name_map = drop_down.id_name_map
            menu = drop_down.menu

            for option in id_name_map:
                menu.add_command(label=id_name_map.get(option),
                                 command=lambda id_=option, value=id_name_map.get(option), column_=column,
                                                entity=relation_entity, drop_down_=drop_down, label_=label:
                                 multi_functions(
                                     self.create_new_relation(column_, value),
                                     self.add_chosen_option(entity, drop_down_, id_, value), label_.grid_forget(),
                                     drop_down_.grid_forget(), self.configure_widget()))

    def add_chosen_option(self, entity, drop_down, id_, value):
        """
        Добавляет опцию в стек.
        :param entity:
        :param drop_down:
        :param id_:
        :param value:
        :return:
        """
        self.chosen_options = drop_down.chosen_options
        self.chosen_options[id_] = value
        self.entity_chosen_option_map[entity] = self.chosen_options

    def create_new_relation(self, column, value):
        """
        Создает новую связь.
        :param column:
        :param value:
        :return:
        """
        for slave in self.grid_slaves(column=column):
            if slave.grid_info()['row'] >= 2:
                label_text = slave.cget('text')

                label = tk.Label(self, text=label_text)
                label.grid(row=slave.grid_info()['row'] + 1, column=column)

                slave.grid_forget()

        tk.Label(self, text=value).grid(row=2, column=column)

    def filter_id_name_map(self, entity, relation_entity, chosen_options, column):
        """
        Обрабатывает значения словаря. Добавляет необходимые связанные сущности из базы данных.
        :param entity:
        :param relation_entity:
        :param chosen_options:
        :param column:
        :return:
        """
        for file_name in RELATION_ENTITY_FILE_NAMES:
            if relation_entity in file_name and self.chosen_option in file_name:
                self.items_to_delete[file_name] = []

                self.file_names.append(file_name)

                self.database.open_database(FILENAME_FOLDER_DICT.get(file_name), file_name)
                db1 = self.database.database

                if db1 is not None and len(db1) > 0:
                    row = 2
                    for item in db1:
                        id_chosen_option = db1[item].__dict__[self.chosen_option]
                        id_relatable_entity = db1[item].__dict__[relation_entity]

                        if id_chosen_option == entity.id_:
                            self.items_to_delete[file_name].append(item)

                            self.database.open_database(FILENAME_FOLDER_DICT.get(relation_entity), relation_entity)
                            db2 = self.database.database

                            for item2 in db2:
                                attributes = self.database.database[item2].__dict__

                                if attributes['id_'] == id_relatable_entity and attributes['id_'] not in chosen_options:
                                    tk.Label(self, text=attributes['name']).grid(row=row, column=column)
                                    row += 1

                                    chosen_options[attributes['id_']] = attributes['name']

                break


class RelationOptionMenu(tk.OptionMenu):
    """
    Меню опций связанных сущностей.
    """

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
        """
        Создает словарь.
        :param chosen_options:
        :return:
        """
        self.database.open_database(FILENAME_FOLDER_DICT.get(self.entity), self.entity)

        self.parent.id_name_map = {}
        id_name_map = self.parent.id_name_map

        db1 = self.database.database
        if db1 is not None and len(db1) > 0:
            for row_index, item in enumerate(db1):
                attributes = db1[item].__dict__

                if self.entity == 'classroom':
                    attr = 'number'
                else:
                    attr = 'name'

                if chosen_options is None or attributes[attr] not in chosen_options:
                    id_name_map[attributes['id_']] = attributes[attr]

                    if self.entity == 'building':
                        id_name_map[attributes['id_']] = \
                            f"{id_name_map[attributes['id_']]} ({attributes['address']})"

                    if self.entity == 'classroom':
                        self.database.open_database('database/database_pickle/entity', 'building')

                        db2 = self.database.database
                        for item2 in db2:
                            if db2[item2].__dict__['id_'] == attributes['building']:
                                id_name_map[attributes['id_']] = \
                                    f"{id_name_map[attributes['id_']]}, {db2[item2].__dict__['name']} " \
                                    f"({db2[item2].__dict__['address']})"

        return id_name_map
