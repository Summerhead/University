import pickle


class EntityDatabase(object):
    def __init__(self, pkl_file_name):
        super().__init__()
        self.filename = 'db_pickle/' + pkl_file_name + '.pkl'
        self.database = {}
        self.index = None
        self.cur_number = None
        self.largest_number = 0
        try:
            self.open_database()
            self.set_initial_attributes_values()
        except:
            self.save_database()

    number = property(lambda self: self.database[self._find_number(self.index)].number)
    balance = property(lambda self: self.database[self._find_number(self.index)].balance)

    def __iter__(self):
        for item in self.database:
            yield self.database[item]

    def set_initial_attributes_values(self):
        if len(self.database) != 0:
            self.index = 0
            keys = list(self.database.keys())
            keys.sort()
            self.largest_number = keys[len(keys) - 1]
        else:
            print('Database is empty')

    def _find_number(self, index):
        keys = list(self.database.keys())
        keys.sort()
        return keys[index]

    def initial(self):
        if len(self.database) == 0:
            return None
        else:
            self.update()
            return self.database[self._find_number(self.index)]

    def next(self):
        if self.index is None:
            return None
        if self.index != len(self.database) - 1:
            self.index += 1
        self.update()
        return self.database[self._find_number(self.index)]

    def prev(self):
        if self.index is None:
            return None
        if self.index != 0:
            self.index -= 1
        self.update()
        return self.database[self._find_number(self.index)]

    def open_database(self):
        with open(self.filename, 'rb') as f:
            self.database = pickle.load(f)

    def save_database(self):
        with open(self.filename, 'wb') as f:
            pickle.dump(self.database, f)

    def add_account(self, balance):
        ba = BankAccount(balance)
        self.largest_number += 1
        if ba.number in self.database:
            ba.number = self.largest_number
        if self.index is None:
            self.index = 0
        else:
            self.index = len(self.database)
        self.database[self.largest_number] = ba
        self.save_database()
        # self.update()

    def delete_account(self, number):
        del self.database[number]
        if len(self.database) == 0:
            self.index = None
            self.cur_number = None
            self.largest_number = 0
        elif self.index != 0:
            self.index -= 1
        self.save_database()
        # self.update()

    def change_balance(self, number, balance):
        account = self.database[number]
        if not account:
            print('Value does not exist')
        account.balance = balance
        self.save_database()
        # self.update()

    def clear_db(self):
        self.database = {}
        self.index = None
        self.cur_number = None
        self.largest_number = 0
        with open(self.filename, 'wb') as f:
            pickle.dump(self.database, f)
