class Rectangle:
    """
    A class representing a rectangle.
    It takes integer values for length and width.
    It is iterable, yielding length then width in a dictionary format.
    """
    def __init__(self, length: int, width: int):
        # We ensure inputs are integers
        if not isinstance(length, int) or not isinstance(width, int):
            raise TypeError("length and width must be integers")
        self.length = length
        self.width = width

    def __iter__(self):
        yield {'length': self.length}
        yield {'width': self.width}
