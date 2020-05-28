import unittest

from view.database import EntityWindow, DatabaseFrame, OPTION_ENTITY_FILEPATH_DICT


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.database_frame = DatabaseFrame()
        self.option = 'Test'
        self.clear_database()
        self.database_frame.configure_table(self.option)
        self.entity_window = EntityWindow(calling_frame=self.database_frame, option=self.option,
                                          database=self.database_frame.database)
        self.entity_window.configure_widget()

        print("Setup finished...\n")

    def populate_database(self, num):
        for _ in range(num):
            self.entity_window.create_new_entity(option=self.option, change=False)

    def delete_item(self, item_num):
        self.database_frame.delete_entity(self.option, item=item_num)

    def clear_database(self):
        self.database_frame.database.clear_database(
            OPTION_ENTITY_FILEPATH_DICT.get(self.option)['filepath']['folder'],
            OPTION_ENTITY_FILEPATH_DICT.get(self.option)['filepath']['file_name'])

    def test_table_frame_configure_header(self):
        self.assertEqual(self.database_frame.table.headers, ['ID', 'Name'])

        print('Test table frame configure header finished successfully.')

    def test_create_entity(self):
        self.clear_database()

        self.populate_database(3)
        print('Database: ')

        self.assertEqual(self.entity_window.database.biggest_id, 3)

        print('New entities created: ')
        self.entity_window.database.print_database()

        self.clear_database()

    def test_delete_entity(self):
        self.clear_database()

        self.populate_database(3)
        print('Database: ')
        self.database_frame.database.print_database()

        item_num = 2
        self.delete_item(item_num)

        self.assertEqual(self.entity_window.database.biggest_id, 3)

        item_num = 3
        self.delete_item(item_num)

        self.assertEqual(self.entity_window.database.biggest_id, 1)

        print('Entity number {0} deleted.'.format(item_num))
        self.database_frame.database.print_database()

        self.clear_database()

    def test_clear_database(self):
        self.clear_database()

        self.populate_database(30)
        print('Database: ')
        self.database_frame.database.print_database()

        self.assertEqual(self.entity_window.database.biggest_id, 30)

        self.clear_database()

        print('Database cleared.')
        self.database_frame.database.print_database()


if __name__ == '__main__':
    unittest.main()
