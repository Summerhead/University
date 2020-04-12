class Pair(object):
    def __init__(self, _id=None, time=None, classroom=None, address=None, subject=None, _type=None, teacher=None,
                 day=None):
        self._id = _id
        self.time = time
        self.classroom = classroom
        self.address = address
        self.subject = subject
        self._type = _type
        self.teacher = teacher
        self.day = day
