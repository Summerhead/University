import pickle
from os import listdir
from os.path import isfile, join


# def create_filename_filepath_dict():
#     dict_ = {}
#     for dir_ in listdir('database/database_pickle/'):
#         dir_path = join('database/database_pickle/', dir_)
#         if not isfile(dir_path):
#             for dir2 in listdir(dir_path):
#                 dir_path2 = join(dir_path, dir2)
#                 if isfile(dir_path2) and dir2 != '__init__.py':
#                     dict_[dir2.replace('.pkl', '')] = dir_path
#     return dict_
#
#
# FILENAME_FILEPATH_DICT = create_filename_filepath_dict()


class Database(object):
    def __init__(self):
        self.database = None
        self.biggest_id = 0

    def open_database(self, folder, file_name):
        try:
            with open(f'{folder}/{file_name}.pkl', 'rb') as f:
                self.database = pickle.load(f)

            self.update_biggest_id()

        except FileNotFoundError:
            with open(f'{folder}/{file_name}.pkl', 'wb'):
                print(f'Creating pickle file \"{folder}/{file_name}.pkl\"')
            self.database = {}
            self.biggest_id = 0

        except EOFError:
            self.database = {}
            self.biggest_id = 0

    def save_database(self, folder, file_name):
        with open(f'{folder}/{file_name}.pkl', 'wb') as f:
            pickle.dump(self.database, f)

        self.update_biggest_id()

    def update_biggest_id(self):
        keys = list(self.database.keys())

        if len(keys) > 0:
            keys.sort()
            self.biggest_id = keys[-1]
        else:
            self.biggest_id = 0

    def increment_biggest_id(self):
        self.biggest_id += 1

    def clear_database(self, folder, file_name):
        self.database = {}
        self.biggest_id = 0

        self.save_database(folder, file_name)
