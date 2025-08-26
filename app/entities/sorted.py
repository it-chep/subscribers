from enum import Enum

class SortedType(str, Enum):
    """Типы сортировки докторов"""
    ASC = "asc"
    DESC = "desc"
