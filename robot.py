from interpreter import variable

# cells = {
#     '▲': 'empty',  # четные
#     '▼': 'empty',  # нечетные
#     '☀': 'exit',
#     '☒': 'wall'
# }
cells = {
    ' ': 'empty',  # четные
    'E': 'exit',
    '#': 'wall'
}

back_cells = {
    'empty': ' ',
    'exit': 'E',
    'wall': '#'
}
''' MATRIX:
Δ ▲▼ ☒ ☆ ☀
    ☒☒☒☒☒☒☒☒☒☒☒☒
    ☒▲▼▲▼▲▼▲▼▲▼☒
    ☒▼▲▼▲▼▲▼▲☆▲☒
    ☒▲▼☀▼▲▼▲▼▲▼☒
    ☒▼▲▼▲▼▲▼▲▼▲☒
    ☒☒☒☒☒☒☒☒☒☒☒☒
'''



class Cell:
    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return f'{self.type}'

class Robot:
    def __init__(self, x, y, right, map):
        self.x = x
        self.y = y
        self._right = right
        self.map = map

    def __repr__(self):
        if self.right:
            return f'x = {self.x}, y = {self.y}; side scan = right\n'
        else:
            return f'x = {self.x}, y = {self.y}; side scan = left\n'

    def show(self):
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if i == self.y and j == self.x:
                    print('☆', end='')
                else:
                    print(back_cells[self.map[i][j].type], end='')
            print()

    def move(self, direction):
        if direction == 'move':
            if (self.x+self.y + 1) % 2 == 0:
                return self.down()
            else:
                return self.up()
        elif direction == 'left':
            return self.left()
        elif direction == 'right':
            return self.right()
        else:
            return variable('int', '', 0)

    def up(self):
        if self.y <= 0:
            return variable('int', '', 0)
        if (self.x + self.y + 1) % 2 == 0:
            return variable('int', '', 0)
        else:
            if self.map[self.y - 1][self.x].type != 'wall':
                self.y -= 1
                return variable('int', '', 1)
        return variable('int', '', 0)

    def down(self):
        if self.y >= len(self.map):
            return variable('int', '', 0)
        if (self.x + self.y + 1) % 2 == 0:
            if self.map[self.y + 1][self.x].type != 'wall':
                self.y += 1
                return variable('int', '', -1)
        return variable('int', '', 0)

    def left(self):
        if self.x <= 0:
            return variable('int', '', 0)
        else:
            if self.map[self.y][self.x - 1].type != 'wall':
                self.x -= 1
                return variable('int', '', -1)
        return variable('int', '', 0)

    def right(self):
        if self.x >= len(self.map[0]):
            return variable('int', '', 0)
        else:
            if self.map[self.y][self.x + 1].type != 'wall':
                self.x += 1
                return variable('int', '', 1)
        return variable('int', '', 0)

    def exit(self):
        if self.map[self.y][self.x].type == 'exit':
            return True
        return False

    def lms(self):
        dist = 1
        length = 5
        if self._right:
            while self.map[self.y][self.x+dist].type == 'empty':
                if length == 0:
                    return variable('int', '', 0)
                dist += 1
                length -= 1
            if self.map[self.y][self.x+dist].type == 'exit':
                return variable('int', '', -dist)
            elif self.map[self.y][self.x+dist].type == 'wall':
                return variable('int', '', dist)
        else:  # left side
            while self.map[self.y][self.x-dist].type == 'empty':
                if length == 0:
                    return variable('int', '', 0)
                dist += 1
                length -= 1
            if self.map[self.y][self.x+dist].type == 'exit':
                return variable('int', '', dist)
            elif self.map[self.y][self.x+dist].type == 'wall':
                return variable('int', '', -dist)

