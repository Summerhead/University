class SchoolClass(object):
    def __init__(self, _id=None, date=None, number=None, classroom=None, subject=None, teacher=None, type_=None):
        self._id = _id
        self.date = date
        self.number = number
        self.classroom = classroom
        self.subject = subject
        self.teacher = teacher
        self.type_ = type_
