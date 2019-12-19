from enum import Enum


class Effects(Enum):
    """ The effects a access control rule can have """
    GRANT = True
    DENY = False
