import os
from seaborn_table import SeabornTable

from .cell import VirtualCell, WindowCell, WallCell, DoorCell
from .diagram import Diagram


class WallTable:
    WALL_FILE_COLUMNS = ['horizontal', 'status', 'room_0', 'room_1',
                         'x0', 'x1', 'y0', 'y1', 'symbols', 'height_1',
                         'height_2', 'window_bottom', 'window_top', 'door',
                         'length']
    EMPTY_CELLS = [Diagram.CHECKER, Diagram.TEN_CHECKER, Diagram.BLANK]

    def __init__(self, wall_file, clear=False):
        self.wall_file = wall_file
        if os.path.exists(wall_file) and not clear:
            self.wall_table = SeabornTable.file_to_obj(
                wall_file, columns=self.WALL_FILE_COLUMNS)
        else:
            self.wall_table = SeabornTable(columns=self.WALL_FILE_COLUMNS)

    def update_wall_file(self, diagram, keep_missing_walls):
        # diagram.remove_virtual()
        diagram.grid = diagram.create_grid()
        diagram.add_layout_to_grid()
        grid = '\n'.join(diagram.grid)
        # todo remove when remove_virtual is done
        for h in VirtualCell.characters:
            grid = grid.replace(h, ' ')

        for room in diagram.rooms:
            room.calc_room_dimensions(diagram.layout, diagram.width * 4,
                                      diagram.height * 2)
        horizontal = self.extract_horizontal_walls(grid, diagram.rooms)
        vertical = self.extract_vertical_walls(grid, diagram.rooms)

        for _row in self.wall_table:
            _row['status'] = 'missing'

        def update_wall(wall):
            for row in self.wall_table:
                if row['status'] == 'missing':
                    matches = [k for k in ['horizontal', 'x0', 'x1', 'y0', 'y1',
                                           'room_0', 'room_1', 'length',
                                           'symbols', 'symbols', 'symbols']
                               if wall.get(k) == row.get(k)]
                    if len(matches) > 6:
                        row.update(wall)
                        row['status'] = 'used'
                        return True
            return False

        for wall in horizontal + vertical:
            if not update_wall(wall):
                self.wall_table.append(dict(status='new', **wall))

        if not keep_missing_walls:
            for i in range(len(self.wall_table)-1, -1, -1):
                wall = self.wall_table[i]
                if wall.get('status') == 'missing' and not any(
                        [wall.get(k) for k in ['height_1', 'height_2', 'door',
                                               'window_bottom', 'window_top']]):
                    self.wall_table.table.pop(i)

        self.wall_table.sort_by_key(('room_0', 'y0', 'x0', 'horizontal'))
        self.wall_table.obj_to_file(self.wall_file, align='left',
                                    quote_numbers=False)

    def extract_horizontal_walls(self, grid, rooms):
        target_cells = [DoorCell.horizontal, WindowCell.horizontal,
                        WallCell.horizontal]
        intersects = [WallCell.top_intersect, WallCell.bottom_intersect,
                      WallCell.internal]
        for v in VirtualCell.characters:
            grid = grid.replace(v, ' ')

        walls = []
        grid = grid.split('\n')
        for y in range(len(grid)):
            symbols = ''
            for x in range(len(grid[y])):
                cell = grid[y][x]
                if cell not in self.EMPTY_CELLS:
                    symbols += cell
                if cell not in target_cells or x == len(grid[y]) - 1:
                    if len(symbols) > 1:
                        if cell in self.EMPTY_CELLS:
                            x -= 1
                        x_start = x - len(symbols) + 1
                        wall = dict(x0=x_start + 1,
                                    x1=x + 1,
                                    y0=y + 1,
                                    length=len(symbols)/4.0,
                                    symbols=symbols,
                                    horizontal=True)
                        wall_rooms = self.extract_rooms(
                            x_start + 1, x - 1, y, y + 1, rooms)
                        if not wall_rooms:
                            print("WARNING: failed to find room for horizontal"
                                  " wall x: %s - %s and y: %s symbols: %s" % (
                                      x_start + 1, x + 1, y + 1, symbols))
                        for i, room in enumerate(wall_rooms):
                            wall[f'room_{i}'] = room
                        walls.append(wall)
                        if symbols[-1] in intersects:
                            symbols = symbols[-1]
                        else:
                            symbols = ''
                    if cell in self.EMPTY_CELLS:
                        symbols = ''
        return walls

    def extract_vertical_walls(self, grid, rooms):
        target_cells = [DoorCell.vertical, WindowCell.vertical,
                        WallCell.vertical]
        intersects = [WallCell.left_intersect, WallCell.right_intersect,
                      WallCell.internal]
        for h in VirtualCell.characters:
            grid = grid.replace(h, ' ')

        walls = []
        grid = grid.split('\n')
        for x in range(len(grid[0])):
            symbols = ''
            for y in range(len(grid)):
                cell = grid[y][x]
                if cell not in self.EMPTY_CELLS:
                    symbols += cell
                if cell not in target_cells or y == len(grid) - 1:
                    if len(symbols) > 1:
                        y_start = y - len(symbols) + 1
                        _symbols = self.convert_vertical_to_horizontal(symbols)
                        wall = dict(x0=x + 1,
                                    y0=y_start + 1,
                                    y1=y + 1,
                                    length=len(symbols)/4.0,
                                    symbols=_symbols,
                                    horizontal=False)
                        wall_rooms = self.extract_rooms(
                            x, x + 1, y_start + 1, y - 1, rooms)
                        # todo remove this hack for stairs
                        if not wall_rooms and symbols == '╬══╩':
                            wall_rooms = ['Stairs']
                        if not wall_rooms:
                            print("WARNING: failed to find room for vertical"
                                  " wall y: %s - %s and x: %s symbols: '%s'" % (
                                      y_start + 1, y + 1, x + 1, _symbols))
                        for i, room in enumerate(wall_rooms):
                            wall[f'room_{i}'] = room
                        walls.append(wall)
                        if symbols[-1] in intersects:
                            symbols = symbols[-1]
                        else:
                            symbols = ''
                    if cell in self.EMPTY_CELLS:
                        symbols = ''
        return walls

    @staticmethod
    def convert_vertical_to_horizontal(symbols):
        # rotate wall counter clockwise
        replacements = {}
        for cls in [WallCell, WindowCell, VirtualCell, DoorCell]:
            replacements[cls.vertical] = cls.horizontal + cls.horizontal
            for _old, _new in [('top_left_corner', 'bottom_left_corner'),
                               ('top_intersect', 'left_intersect'),
                               ('top_right_corner', 'top_left_corner'),
                               ('bottom_left_corner', 'bottom_right_corner'),
                               ('bottom_intersect', 'right_intersect'),
                               ('bottom_right_corner', 'top_right_corner'),
                               ('left_intersect', 'bottom_intersect'),
                               ('right_intersect', 'top_intersect')
                               ]:
                if getattr(cls, _old, None) and getattr(cls, _new, None):
                    replacements[getattr(cls, _old)] = getattr(cls, _new)

        return ''.join([replacements.get(s, s) for s in symbols])

    @staticmethod
    def extract_rooms(x_start, x_end, y_start, y_end, rooms):
        def room_found(room):
            if not room.walls:
                return False
            for x in range(x_start, x_end):
                for y in range(y_start, y_end):
                    if (x, y) in room.walls:
                        return True
            return False

        return [room.name for room in rooms if room_found(room)]

    def recreate_diagram_file(self, filename):
        walls = [wall for wall in self.wall_table if wall.status != 'missing']
        width = max([wall.x + len(wall.symbols) for wall in walls
                     if wall.horizontal])
        height = max([wall.y + len(wall.symbols) for wall in walls
                      if not wall.horizontal])
        grid = [[' ' for w in width] for h in height]
        for wall in self.wall_table:
            if wall.horizontal:
                for i, s in enumerate(wall.symbols):
                    grid[wall.y][wall.x + i] = s
            else:
                for i, s in enumerate(wall.symbols):
                    grid[wall.y + i][wall.x] = s
        with open(filename, 'w') as fn:
            fn.write('\n'.join([''.join(row) for row in grid]))

    def __iter__(self):
        return self.wall_table.__iter__()
