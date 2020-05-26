import unittest

from view.database import EntityWindow, DatabaseFrame, OPTION_ENTITY_FILEPATH_DICT


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.database_frame = DatabaseFrame()
        self.option = 'Test'
        self.database_frame.configure_table(self.option)
        self.entity_window = EntityWindow(calling_frame=self.database_frame, option=self.option,
                                          database=self.database_frame.database)
        self.entity_window.configure_widget()

        print("Setup finished...\n")

    def test_table_frame_configure_header(self):
        self.assertEqual(self.database_frame.table.headers, ['ID', 'Name'])

        print('Test table frame configure header finished successfully.')

    def test_create_entity(self):
        print('database: ', self.entity_window.database.database)
        for _ in range(3):
            self.entity_window.create_new_entity(option=self.option, change=False)

        print('New entities created: ')
        self.entity_window.database.print_database()

    def test_delete_entity(self):
        self.database_frame.delete_entity(self.option, item=2)

        print('Entity number 2 deleted.')
        self.database_frame.database.print_database()

    def test_clear_database(self):
        self.database_frame.database.print_database()

        self.database_frame.database.clear_database(
            OPTION_ENTITY_FILEPATH_DICT.get(self.option)['filepath']['folder'],
            OPTION_ENTITY_FILEPATH_DICT.get(self.option)['filepath']['file_name'])

        print('Database cleared.')
        self.database_frame.database.print_database()


if __name__ == '__main__':
    unittest.main()
