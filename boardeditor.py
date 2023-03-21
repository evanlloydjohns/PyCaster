import pygame
import random


ON = 1
OFF = 0

WIDTH = 800
HEIGHT = 800
CELL_COUNT = 20
FRAME_RATE = 30
CURRENT_BOARD = "PyCasterEditor"


class Cell:
    """Cell class is used for creating individual entries in a board object

    Attributes:
        row: the row the cell is in
        col: the column the cell is in
        size: the size of the cell
        rect: the drawable object that represents the cell
        color: the color of the cell
    """
    def __init__(self, row, col, size):
        """Inits Cell with row, column, rect, color, and cell size"""
        self.row = row
        self.col = col
        self.size = size
        self.rect = pygame.Rect(row, col, size, size)
        self.color = (0, 0, 0)

    def get_rect(self):
        return self.rect

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color


class Tile(Cell):
    """Tile is a type of cell that is used in the Mazectric and GameOfLife boards

    Attributes:
        row: the row the Tile is in
        col: the column the Tile is in
        size: the size of the Tile
        color: the color of the Tile
        state: Current state of the tile (either ON or OFF)
    """

    def __init__(self, row, col, size):
        """Inits Tile with row, column, starting state, color, and cell size"""
        super().__init__(row, col, size)
        self.color = (0, 0, 0)
        self.state = OFF

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state
        self.update_color()

    def update_color(self):
        if self.state == ON:
            self.color = (255, 255, 255)
        elif self.state == OFF:
            self.color = (0, 0, 0)


class Player(Cell):
    """Player is a type of cell that can be moved around a board

    Attributes:
        row: the row the Player is in
        col: the column the Player is in
        size: the size of the Player
        color: the color of the cell
    """

    def __init__(self, row, col, size):
        """Inits Player with row, column, color, and cell size"""
        super().__init__(row, col, size)
        self.color = (255, 0, 0)

    def get_row(self):
        return self.row

    def set_row(self, row):
        """Updates the row and rect location"""
        self.row = row
        self.rect.x = self.row * self.size

    def get_col(self):
        return self.col

    def set_col(self, col):
        """Updates the col and rect location"""
        self.col = col
        self.rect.y = self.col * self.size

    def get_size(self):
        return self.size


class Board:
    """Represents the current game state

    Attributes:
        tile_count: total number of rows/columns
        tile_size: size of each tile
        width: width of the board
        height: height of the board
    """

    def __init__(self, tile_count, tile_size, width, height, random_gen):
        """Inits Board with tile_count, tile_size, width, and height"""
        self.tile_count = tile_count
        self.tile_size = tile_size
        self.width = width
        self.height = height
        self.tiles = []
        self.gen(random_gen)

    def process_inputs(self):
        """Processes all user inputs"""
        pass

    def update(self):
        """Processes next board state"""
        pass

    def process_outputs(self):
        """Outputs current board state"""
        pass

    def get_neighbor_counts(self):
        """Returns list of each tile's neighbor count"""
        counts = []
        # Utilize python's index wrapping in lists to find each cell's neighbor count
        adj_table = [(-1, -1), (0, -1), (1, -1), (-1,  0), (1,  0), (-1,  1), (0,  1), (1,  1)]
        for i in range(self.tile_count):
            t = []
            for j in range(self.tile_count):
                c = 0
                for x, y in adj_table:
                    ix = (i + x) % self.tile_count
                    jy = (j + y) % self.tile_count
                    c += self.tiles[ix][jy].get_state()
                t.append(c)
            counts.append(t)
        return counts

    def gen(self, random_gen):
        """Inits the board's tiles"""
        self.tiles.clear()
        if random_gen:
            for c in range(self.tile_count):
                temp = []
                for r in range(self.tile_count):
                    tile = Tile(c * self.tile_size, r * self.tile_size, self.tile_size)
                    tile.set_state(random.randint(0, 1))
                    temp.append(tile)
                self.tiles.append(temp)
        else:
            for c in range(self.tile_count):
                temp = []
                for r in range(self.tile_count):
                    tile = Tile(c * self.tile_size, r * self.tile_size, self.tile_size)
                    tile.set_state(0)
                    temp.append(tile)
                self.tiles.append(temp)

    def draw(self):
        """Draws the current board state to the display"""
        screen = pygame.display.get_surface()
        line_width = 1
        # Draw the tiles
        for c in range(self.tile_count):
            for r in range(self.tile_count):
                tile = self.tiles[c][r]
                pygame.draw.rect(screen, tile.get_color(), tile.get_rect())
        # Draw horizontal dividing lines
        for i in range(self.tile_count + 1):
            p1 = i * self.tile_size, 0
            p2 = i * self.tile_size, self.height
            pygame.draw.line(screen, (15, 15, 15), p1, p2, line_width)
        # Draw vertical dividing lines
        for i in range(self.tile_count + 1):
            p1 = 0, i * self.tile_size
            p2 = self.width, i * self.tile_size
            pygame.draw.line(screen, (15, 15, 15), p1, p2, line_width)

    def debug(self):
        """Draws a debug overlay with each tile's neighbor count"""
        counts = self.get_neighbor_counts()
        screen = pygame.display.get_surface()
        font = pygame.font.SysFont('Helvetica.ttf', 32)
        for c in range(self.tile_count):
            for r in range(self.tile_count):
                count = counts[c][r]
                pos = c * self.tile_size, r * self.tile_size
                text = font.render(str(count), True, (127, 127, 127))
                screen.blit(text, pos)

    def flip_tile_at_loc(self, pos):
        """Toggles a tile's state at the given position"""
        for i in range(self.tile_count):
            for j in range(self.tile_count):
                rect = self.tiles[i][j].get_rect()
                if rect.collidepoint(pos):
                    self.tiles[i][j].set_state(int(not bool(self.tiles[i][j].get_state())))


class PyCasterEditor(Board):
    """Form of the Board class which supports saving of the board state for PyCaster engine

        Attributes:
            tile_count: total number of rows/columns
            tile_size: size of each tile
            width: width of the board
            height: height of the board
    """

    def __init__(self, tile_count, tile_size, width, height):
        """Inits board with tile_count, tile_size, width, and height"""
        super().__init__(tile_count, tile_size, width, height, False)

    def update(self):
        """Processes next board state"""

        return False

    def process_inputs(self):
        """Processes user inputs"""
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.flip_tile_at_loc(pygame.mouse.get_pos())
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    self.save_board("board.txt")
        return True

    def save_board(self, filename):
        """Saves the current board state"""
        # iterate through the tiles
        with open(filename, 'w') as file:
            data = ""
            tile_set = "default"
            walls = []
            for c in range(self.tile_count):
                for r in range(self.tile_count):
                    tile = self.tiles[c][r]
                    if tile.get_state() == ON:
                        # get all points of the tile
                        x = tile.get_rect().x
                        y = tile.get_rect().y
                        w = tile.get_rect().w
                        h = tile.get_rect().h
                        p1 = ((x + 0) / self.tile_size) * 10, ((y + 0) / self.tile_size) * 10
                        p2 = ((x + w) / self.tile_size) * 10, ((y + 0) / self.tile_size) * 10
                        p3 = ((x + w) / self.tile_size) * 10, ((y + h) / self.tile_size) * 10
                        p4 = ((x + 0) / self.tile_size) * 10, ((y + h) / self.tile_size) * 10
                        ps = [p1, p2, p3, p4]
                        # Add tile walls to walls list
                        for i in range(len(ps)):
                            walls.append((ps[i], ps[(i+1) % len(ps)]))
            # remove any redundant walls from the list
            print(len(walls))
            self.cull_redundant_walls(walls)
            print(len(walls))
            # write walls to file
            for wall in walls:
                data += f"{tile_set}: {wall[0]}; {wall[1]}; {(255, 255, 255)}\n"
            # Remove trailing newline
            data = data[0:len(data) - 1]
            file.write(data)
            file.close()

    def cull_redundant_walls(self, walls: list):
        redundant_walls = []
        for i in range(len(walls)):
            w1 = walls[i]
            for j in range(i+1, len(walls)):
                w2 = walls[j]
                if w1[0] == w2[0] and w1[1] == w2[1]:
                    redundant_walls.append(w1)
                elif w1[0] == w2[1] and w1[1] == w2[0]:
                    redundant_walls.append(w1)
        for r_wall in redundant_walls:
            walls.remove(r_wall)

    def process_outputs(self):
        self.draw()


BOARDS = {"PyCasterEditor": PyCasterEditor}


class BoardEditor:
    """Main class that handles/organizes the board and the main loop

    Attributes:
        width: width of the window
        height: height of the window
        cell_count: total number of cells in each column/row
        frame_rate: maximum number of frames do be drawn each second
        board_name: type of board the game will be running
    """

    def __init__(self, width, height, cell_count, frame_rate, board_name):
        """Inits current game with width, height, cell_count, frame_rate, and board_name"""
        self.width = width
        self.height = height
        self.cell_count = cell_count
        self.frame_rate = frame_rate
        self.cell_size = ((self.width / self.cell_count) + (self.height / self.cell_count)) / 2
        self.board = BOARDS[board_name](self.cell_count, self.cell_size, self.width, self.height)
        pygame.init()
        pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(board_name)
        # Used for frame limiting the window
        self.clock = pygame.time.Clock()
        # Used in exiting game loop
        self.running = True
        # Allows user to display a debug overlay
        self.is_debug = False
        # Determines whether player has won
        self.win_condition = False

    def draw(self):
        """Draws any overlays"""
        # Draw board's debug if player turned on debug
        if self.is_debug:
            self.board.debug()
        # If player has won, then display win message
        if self.win_condition:
            screen = pygame.display.get_surface()
            font = pygame.font.SysFont('Helvetica.ttf', 128)
            text = font.render("You Win!", True, (255, 0, 0))
            screen.blit(text, (self.width / 4, self.height / 4))
        pygame.display.flip()

    def process_inputs(self):
        """Processes user inputs"""
        # Don't process board input if player has won
        if not self.win_condition:
            self.running = self.board.process_inputs()
        # Check for debug key and exit condition
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.running = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.is_debug = not self.is_debug
                if event.key == pygame.K_r:
                    if self.win_condition:
                        self.__init__(WIDTH, HEIGHT, CELL_COUNT, FRAME_RATE, CURRENT_BOARD)

    def update(self):
        """Processes the board and checks win condition"""
        self.win_condition = self.board.update()

    def process_outputs(self):
        """Processes all outputs"""
        self.board.process_outputs()
        self.draw()

    def loop(self):
        """Main game loop"""
        while self.running:
            self.process_inputs()
            self.update()
            self.process_outputs()
            self.clock.tick(self.frame_rate)
        pygame.quit()


if __name__ == "__main__":
    editor = BoardEditor(WIDTH, HEIGHT, CELL_COUNT, FRAME_RATE, CURRENT_BOARD)
    editor.loop()
