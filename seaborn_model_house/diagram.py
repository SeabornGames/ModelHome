from collections import OrderedDict
from seaborn_table import SeabornTable
from .cell import (DoorCell, VirtualCell, WindowCell, WallCell,
                   RoomName, ObjectName)


class Diagram:
    CHECKER = '░'
    TEN_CHECKER = '▒'
    BLANK = ' '

    def __init__(self, input_file, checker=False, width=None, height=None):
        self.layout = OrderedDict()
        self.name_characters = OrderedDict()
        self.rooms = []
        self.objects = []
        self.width = width
        self.height = height
        self.checker = self.CHECKER if checker else self.BLANK
        self.ten_checker = self.TEN_CHECKER if checker else self.BLANK
        self.blank = self.BLANK
        if input_file:
            self.parse_file(input_file)
        self.grid = self.create_grid()

    def get_room(self, room_name):
        for room in self.rooms:
            if room.name == room_name:
                return room

    def create_grid(self):
        grid = []
        odd = even = ''
        for w in range(self.width):
            odd += (self.blank * 4) if w % 2 else (self.checker * 4)
            if w % 10 == 9:
                even += self.ten_checker * 4
            else:
                even += (self.checker * 4) if w % 2 else (self.blank * 4)
        for i in range(self.height):
            if i % 10 == 9:
                grid += [odd.replace(self.checker, self.ten_checker)] * 2
            else:
                grid += [odd, odd] if i % 2 else [even, even]
        return grid

    def parse_file(self, input_file):
        with open(input_file, 'r') as fn:
            grid = fn.read().split('\n')
        if grid[0].startswith('     000000'):  # then strip header:
            grid = [row[5:] for row in grid[3:]]

        if self.height is None:
            self.height = (len(grid)+1) // 2
        else:
            grid = grid[:self.height * 2]
        if self.width is None:
            self.width = (max(*[len(g) for g in grid])+3) // 4
        else:
            grid = [g[:self.width * 4] for g in grid]

        for y, row in enumerate(grid):
            for x, c in enumerate(row):
                if c in [self.blank, self.checker, self.ten_checker]:
                    pass
                elif c in DoorCell.characters:
                    self.layout[x, y] = DoorCell(c, x, y)
                elif c in VirtualCell.characters:
                    self.layout[x, y] = VirtualCell(c, x, y)
                elif c in WindowCell.characters:
                    self.layout[x, y] = WindowCell(c, x, y)
                elif c in WallCell.characters:
                    self.layout[x, y] = WallCell(c, x, y)
                elif c in RoomName.characters:
                    self.name_characters[x, y] = RoomName(c, x, y)
                elif c in ObjectName.characters:
                    self.name_characters[x, y] = ObjectName(c, x, y)

        for cell in self.layout.values():
            cell.clean(diagram=self)
        for k in list(self.name_characters.keys()):
            v = self.name_characters.get(k)
            if v is not None:  # character was popped out with other names
                v.clean(diagram=self)

    def remove_objects(self):
        self.layout = self.create_room_only_layout()
        self.objects.clear()
        for v in self.layout.values():
            v.clean(self)

    def remove_virtual(self):
        """This will remove the virtual walls and then clean the layout,
           If a wall would be turned into vertical or horizontal line
           then it will be replaced with a special vertical_break or
           horizontal_break, so that the wall_file still breaks the two walls"""
        for key, cell in list(self.layout.items()):
            if isinstance(cell, VirtualCell):
                self.layout.pop(key)
        for cell in self.layout.values():
            cell.clean(diagram=self, keep_break=True)

    def create_room_only_layout(self):
        room_layout = OrderedDict()
        removed_walls = []
        for obj in self.objects:
            if not obj.walls:
                obj.calc_room_dimensions(self.layout, self.width * 4,
                                         self.height * 2)
            for location in obj.walls:
                wall = self.layout.get(location)
                if isinstance(wall, VirtualCell) and wall not in removed_walls:
                    removed_walls.append(wall)
        for k, v in self.layout.items():
            if v not in removed_walls:
                room_layout[k] = v
        return room_layout

    def add_names_to_grid(self):
        for room in self.rooms:
            room.add_name_to_grid(diagram=self)
        for obj in self.objects:
            obj.add_name_to_grid(diagram=self)

    def add_layout_to_grid(self):
        for v in self.layout.values():
            row = self.grid[v.y]
            self.grid[v.y] = row[:v.x] + v.c + row[v.x + 1:]

    def add_ruler(self):
        header = [' ' * 5] * 3
        for w in range(self.width):
            header[0] += str(w // 10)[-1] + str(w // 10)[-1] + str(w // 10)[
                -1] + str(
                w // 10)[-1]
        for w in range(self.width):
            header[1] += str(w % 10) + str(w % 10) + str(w % 10) + str(w % 10)
        header[2] += ' ¼½¾' * self.width
        for i, row in enumerate(self.grid):
            self.grid[i] = str(i // 2).rjust(4, ' ') + [' ', '½'][i % 2] + \
                           self.grid[i]
        self.grid = header + self.grid

    def square_footage(self):
        table = SeabornTable(columns=['Room', 'SQFT'])
        total = []
        for room in self.rooms:
            room.calc_room_dimensions(self.layout, self.width*4, self.height*2)
            total += room.cells + room.walls
            table.append([room.name, len(room.cells) / 8])
        table.append(['TOTAL', len(set(total)) / 8])
        return table

    def __str__(self):
        return '\n'.join(self.grid)

    def save_to_file(self, filename):
        if filename and filename != '-':
            with open(filename, 'w') as fn:
                fn.write(str(self))
        else:
            print(self)
