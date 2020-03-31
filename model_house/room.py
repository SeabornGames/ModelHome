class Room:
    horizontal_buffer = ' '
    vertical_buffer = ' '
    buffer_size = 2

    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.cells = []
        self.walls = []

    def __repr__(self):
        return 'Room<%s, %s, %s>' % (self.name, self.x, self.y)

    def __str__(self):
        return self.name

    def calc_room_dimensions(self, layout, max_x, max_y):
        self.cells = []
        self.walls = []
        self.cells.append((self.x, self.y))
        i = 0
        done = set()
        while i < len(self.cells):
            x, y = self.cells[i]
            for neighbor in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),
                             (x - 1, y - 1), (x + 1, y + 1), (x + 1, y - 1),
                             (x - 1, y + 1)]:
                if not (0 <= neighbor[0] < max_x):
                    continue
                if not (0 <= neighbor[1] < max_y):
                    continue
                if neighbor in done:
                    continue
                done.add(neighbor)
                cell = layout.get(neighbor)
                if cell is None:
                    self.cells.append(neighbor)
                else:
                    self.walls.append(neighbor)
            i += 1

    def highlight(self, diagram, color='░'):
        if not self.cells:
            self.calc_room_dimensions(diagram.layout, diagram.width * 4,
                                      diagram.height * 2)

        for x, y in self.cells:
            if diagram.grid[y][x] == ' ':
                row = diagram.grid[y]
                diagram.grid[y] = row[:x] + color + row[x + 1:]

    def add_name_to_grid(self, diagram):
        i = len(self.name)
        l = r = 0
        for r in range(self.x + i, min(diagram.width * 4, self.x + i + 400)):
            if diagram.layout.get((r, self.y), None):
                break
        for l in range(self.x, max(-1, self.x - 400), -1):
            if l and diagram.layout.get((l, self.y), None):
                break
        name = (self.vertical_buffer * self.buffer_size + self.name.strip() +
                self.vertical_buffer * self.buffer_size)
        _ljust = (r - l - len(name)) // 2 + 1
        indexes = [self.y]
        for r in range(1, self.buffer_size + 1):
            if (self.x, self.y + r) in self.cells:
                indexes.append(self.y + r)
            if (self.x, self.y - r) in self.cells:
                indexes.append(self.y - r)
        for r in indexes:
            if 0 <= r < len(diagram.grid):
                row = diagram.grid[r]
                left_side = row[:l + _ljust]
                right_side = row[l + _ljust + len(name):]
                diagram.grid[r] = left_side + name + right_side
                name = self.horizontal_buffer * len(name)


class Object(Room):
    pass
