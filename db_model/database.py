import pickle


class Database(object):
    def __init__(self):
        self.database = None
        self.biggest_id = 0

    def open_database(self, option):
        try:
            with open('db_pickle/' + option.lower() + '.pkl', 'rb') as f:
                self.database = pickle.load(f)

            self.update_biggest_id()

        except FileNotFoundError:
            with open('db_pickle/' + option.lower() + '.pkl', 'wb'):
                print("Creating pickle file \"db_pickle/" + option.lower() + ".pkl\"")
            self.database = {}
            self.biggest_id = 0

        except EOFError:
            self.database = {}
            self.biggest_id = 0

    def save_database(self, option):
        with open('db_pickle/' + option.lower() + '.pkl', 'wb') as f:
            pickle.dump(self.database, f)

    def update_biggest_id(self):
        keys = list(self.database.keys())
        keys.sort()
        self.biggest_id = keys[-1]
