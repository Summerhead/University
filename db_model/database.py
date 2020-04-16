import pickle


class Database(object):
    def __init__(self):
        self.database = None
        self.biggest_id = 0

    def open_database(self, folder, file_name):
        try:
            with open(f'db_pickle/{folder}/{file_name}.pkl', 'rb') as f:
                self.database = pickle.load(f)

            self.update_biggest_id()

        except FileNotFoundError:
            with open(f'db_pickle/{folder}/{file_name}.pkl', 'wb'):
                print(f'Creating pickle file \"db_pickle/{folder}/{file_name}.pkl\"')
            self.database = {}
            self.biggest_id = 0

        except EOFError:
            self.database = {}
            self.biggest_id = 0

    def save_database(self, folder, file_name):
        with open(f'db_pickle/{folder}/{file_name}.pkl', 'wb') as f:
            pickle.dump(self.database, f)

        self.update_biggest_id()

    def update_biggest_id(self):
        keys = list(self.database.keys())
        keys.sort()
        try:
            self.biggest_id = keys[-1]
        except IndexError:
            self.biggest_id = 0

    def increment_biggest_id(self):
        self.biggest_id += 1

    def clear_database(self, folder, file_name):
        self.database = {}
        self.biggest_id = 0
        self.save_database(folder, file_name)
