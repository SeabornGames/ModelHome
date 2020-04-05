from .room import Room, Object


class Cell:
    def __init__(self, c, x, y):
        self.c = c
        self.x = x
        self.y = y

    def __repr__(self):
        return '%s<%r, %r, %r>' % (self.__class__.__name__,
                                   self.c, self.x, self.y)

    def __str__(self):
        return self.c

    def clean(self, diagram, keep_break=False):
        if (self.x, self.y + 1) in diagram.layout:
            if (self.x, self.y - 1) in diagram.layout:
                if (self.x - 1, self.y) in diagram.layout:
                    if (self.x + 1, self.y) in diagram.layout:
                        self.c = self.internal
                    else:  # not right
                        self.c = self.right_intersect
                else:  # not left
                    if (self.x + 1, self.y) in diagram.layout:
                        self.c = self.left_intersect
                    elif keep_break and self.c != self.vertical:
                        self.c = self.vertical_break
                    else: # not right or left
                        self.c = self.vertical
            else:  # not below
                if (self.x - 1, self.y) in diagram.layout:
                    if (self.x + 1, self.y) in diagram.layout:
                        self.c = self.top_intersect
                    else:  # not right
                        self.c = getattr(self, 'top_right_corner', self.c)
                else:  # not left
                    if (self.x + 1, self.y) in diagram.layout:
                        self.c = getattr(self, 'top_left_corner', self.c)
                    else:  # not right
                        pass
        else:  # not above
            if (self.x, self.y - 1) in diagram.layout:
                if (self.x - 1, self.y) in diagram.layout:
                    if (self.x + 1, self.y) in diagram.layout:
                        self.c = self.bottom_intersect
                    else:  # not right
                        self.c = getattr(self, 'bottom_right_corner', self.c)
                else:  # not left
                    if (self.x + 1, self.y) in diagram.layout:
                        self.c = getattr(self, 'bottom_left_corner', self.c)
                    else:  # not right or left
                        pass
            else:  # not below
                if (self.x - 1, self.y) in diagram.layout:
                    if (self.x + 1, self.y) in diagram.layout:
                        if keep_break and self.c != self.horizontal:
                            self.c = self.horizontal_break
                        else:
                            self.c = self.horizontal
                    else:  # not right
                        pass
                else:  # not left
                    pass


class RoomName(Cell):
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789[]_-'

    def combine_characters_to_a_name(self, diagram):
        # This will remove this character and other name characters from
        # diagram.names
        name = ''
        for i in range(100):
            _next = diagram.name_characters.get((self.x + i, self.y), None)
            if isinstance(_next, RoomName):
                diagram.name_characters.pop((self.x + i, self.y))
                name += _next.c
            elif (_next is None and (self.x + i, self.y) not in diagram.layout
                  and name[-1] != ' '):
                name += ' '
            else:
                break
        return name.strip()

    def clean(self, diagram):
        name = self.combine_characters_to_a_name(diagram)
        diagram.rooms.append(Room(name, self.x, self.y))


class ObjectName(RoomName):
    characters = 'abcdefghijklmnopqrstuvwxyz'

    def clean(self, diagram):
        name = self.combine_characters_to_a_name(diagram)
        diagram.objects.append(Object(name, self.x, self.y))


class DoorCell(Cell):
    horizontal = '▤'
    internal = '⏹'
    left_intersect = '⏹'
    right_intersect = '⏹'
    top_intersect = '⏹'
    bottom_intersect = '⏹'
    vertical = '█'
    characters = (horizontal + internal + left_intersect + right_intersect +
                  top_intersect + bottom_intersect + vertical + vertical)


class VirtualCell(Cell):
    horizontal = '┈'
    internal = '⟊'
    left_intersect = '┆'
    right_intersect = '┆'
    top_intersect = '┈'
    bottom_intersect = '┈'
    vertical = '┆'
    top_right_corner = '┐'
    top_left_corner = '┌'
    bottom_right_corner = '┘'
    bottom_left_corner = '└'
    characters = (horizontal + internal + left_intersect + right_intersect +
                  top_intersect + bottom_intersect + vertical +
                  top_right_corner + top_left_corner + bottom_left_corner +
                  bottom_right_corner)


class WindowCell(Cell):
    horizontal = '─'
    internal = '┼'
    left_intersect = '╟'
    right_intersect = '╢'
    top_intersect = '╤'
    bottom_intersect = '╧'
    vertical = '│'
    characters = (horizontal + internal + left_intersect + right_intersect +
                  top_intersect + bottom_intersect + vertical)


class WallCell(Cell):
    horizontal = '═'
    horizontal_break = '╪'
    internal = '╬'
    top_left_corner = '╔'
    top_intersect = '╦'
    top_right_corner = '╗'
    bottom_left_corner = '╚'
    bottom_intersect = '╩'
    bottom_right_corner = '╝'
    left_intersect = '╠'
    vertical = '║'
    vertical_break = '╫'
    right_intersect = '╣'
    characters = (horizontal + internal + left_intersect + right_intersect +
                  top_intersect + bottom_intersect + vertical +
                  top_left_corner + top_right_corner + bottom_left_corner +
                  bottom_right_corner)


class ObjectCell(Cell):
    horizontal = '━'
    internal = '╋'
    top_left_corner = '┏'
    top_intersect = '┳'
    top_right_corner = '┓'
    bottom_left_corner = '┗'
    bottom_intersect = '┻'
    bottom_right_corner = '┛'
    left_intersect = '┣'
    vertical = '┃'
    right_intersect = '┫'
    characters = (horizontal + internal + left_intersect + right_intersect +
                  top_intersect + bottom_intersect + vertical +
                  top_left_corner + top_right_corner + bottom_left_corner +
                  bottom_right_corner)
