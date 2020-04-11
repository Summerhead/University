from db_model.entity_database import EntityDatabase


class CollegeDatabase(EntityDatabase):
    def __init__(self):
        super().__init__(pkl_file_name='college')
