import enum


class Effects(enum.Enum):
    """ The effects a access control rule can have """
    GRANT = True
    DENY = False

    def __str__(self):
        return str(self.name)
