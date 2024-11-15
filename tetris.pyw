import tkinter as tk
import random

class TetrisGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tetris")
        
        # Constants
        self.GAME_WIDTH = 300
        self.GAME_HEIGHT = 600
        self.CELL_SIZE = 30
        self.GRID_WIDTH = 10
        self.GRID_HEIGHT = 20
        self.BASE_SPEED = 500  # Base falling speed in milliseconds
        
        # Colors
        self.COLORS = [
            "#00FFFF",  # Cyan
            "#FFFF00",  # Yellow
            "#800080",  # Purple
            "#00FF00",  # Green
            "#FF0000",  # Red
            "#0000FF",  # Blue
            "#FF7F00"   # Orange
        ]
        
        # Tetromino shapes
        self.SHAPES = [
            [[1, 1, 1, 1]],  # I
            [[1, 1], [1, 1]],  # O
            [[1, 1, 1], [0, 1, 0]],  # T
            [[1, 1, 0], [0, 1, 1]],  # S
            [[0, 1, 1], [1, 1, 0]],  # Z
            [[1, 1, 1], [1, 0, 0]],  # L
            [[1, 1, 1], [0, 0, 1]]   # J
        ]
        
        # Game state
        self.paused = False
        self.game_over = True
        self.score = 0
        self.level = 1
        self.speed = self.BASE_SPEED
        
        # Create menu
        self.create_menu()
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.GAME_WIDTH,
            height=self.GAME_HEIGHT,
            bg="black"
        )
        self.canvas.pack(padx=10, pady=10)
        
        # Create score and level display
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(fill=tk.X, padx=10)
        
        self.score_label = tk.Label(
            self.info_frame,
            text=f"Score: {self.score}",
            font=("Arial", 16)
        )
        self.score_label.pack(side=tk.LEFT, padx=10)
        
        self.level_label = tk.Label(
            self.info_frame,
            text=f"Level: {self.level}",
            font=("Arial", 16)
        )
        self.level_label.pack(side=tk.RIGHT, padx=10)
        
        # Bind keys
        self.root.bind("<Key>", self.handle_keypress)
        
        # Make window non-resizable
        self.root.resizable(False, False)
        
        # Initialize game grid
        self.reset_game()
        
        # Start game loop
        self.update()
    
    def create_menu(self):
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Game menu
        game_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game", command=lambda: self.reset_game())
        game_menu.add_separator()
        game_menu.add_command(label="Quit", command=self.root.quit)
    
    def reset_game(self):
        self.grid = [[None for _ in range(self.GRID_WIDTH)] for _ in range(self.GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.speed = self.BASE_SPEED
        self.game_over = False
        self.paused = False
        self.score_label.config(text=f"Score: {self.score}")
        self.level_label.config(text=f"Level: {self.level}")
        self.new_piece()
    
    def new_piece(self):
        # Select random shape and color
        self.current_shape = random.choice(self.SHAPES)
        self.current_color = random.choice(self.COLORS)
        self.current_x = self.GRID_WIDTH // 2 - len(self.current_shape[0]) // 2
        self.current_y = 0
        
        if self.check_collision():
            self.game_over = True
    
    def rotate_piece(self):
        # Create rotated shape
        rows = len(self.current_shape)
        cols = len(self.current_shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows-1-r] = self.current_shape[r][c]
        
        if not self.check_collision(rotated, self.current_x, self.current_y):
            self.current_shape = rotated
    
    def check_collision(self, shape=None, offset_x=None, offset_y=None):
        shape = shape or self.current_shape
        offset_x = self.current_x if offset_x is None else offset_x
        offset_y = self.current_y if offset_y is None else offset_y
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pos_x = offset_x + x
                    pos_y = offset_y + y
                    if (pos_x < 0 or pos_x >= self.GRID_WIDTH or
                        pos_y >= self.GRID_HEIGHT or
                        (pos_y >= 0 and self.grid[pos_y][pos_x] is not None)):
                        return True
        return False
    
    def lock_piece(self):
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    if self.current_y + y >= 0:
                        self.grid[self.current_y + y][self.current_x + x] = self.current_color
        
        self.clear_lines()
        self.new_piece()
    
    def clear_lines(self):
        lines_cleared = 0
        y = self.GRID_HEIGHT - 1
        while y >= 0:
            if all(cell is not None for cell in self.grid[y]):
                lines_cleared += 1
                for move_y in range(y, 0, -1):
                    self.grid[move_y] = self.grid[move_y - 1][:]
                self.grid[0] = [None] * self.GRID_WIDTH
            else:
                y -= 1
        
        if lines_cleared:
            self.score += (lines_cleared * 100) * lines_cleared
            self.score_label.config(text=f"Score: {self.score}")
            
            # Level up every 1000 points
            new_level = (self.score // 1000) + 1
            if new_level != self.level:
                self.level = new_level
                self.speed = max(100, self.BASE_SPEED - (self.level - 1) * 50)
                self.level_label.config(text=f"Level: {self.level}")
    
    def draw(self):
        self.canvas.delete("all")
        
        # Draw grid
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                color = self.grid[y][x] or "black"
                self.canvas.create_rectangle(
                    x * self.CELL_SIZE,
                    y * self.CELL_SIZE,
                    (x + 1) * self.CELL_SIZE,
                    (y + 1) * self.CELL_SIZE,
                    fill=color,
                    outline="gray"
                )
        
        # Draw current piece
        if not self.game_over and not self.paused:
            for y, row in enumerate(self.current_shape):
                for x, cell in enumerate(row):
                    if cell:
                        self.canvas.create_rectangle(
                            (self.current_x + x) * self.CELL_SIZE,
                            (self.current_y + y) * self.CELL_SIZE,
                            (self.current_x + x + 1) * self.CELL_SIZE,
                            (self.current_y + y + 1) * self.CELL_SIZE,
                            fill=self.current_color,
                            outline="white"
                        )
        
        # Draw messages
        if self.game_over:
            self.canvas.create_text(
                self.GAME_WIDTH // 2,
                self.GAME_HEIGHT // 2,
                text="Game Over!\nPress F1 for new game",
                fill="white",
                font=("Arial", 24),
                justify="center"
            )
        elif self.paused:
            self.canvas.create_text(
                self.GAME_WIDTH // 2,
                self.GAME_HEIGHT // 2,
                text="PAUSED\nPress ESC to continue",
                fill="white",
                font=("Arial", 24),
                justify="center"
            )
    
    def handle_keypress(self, event):
        if event.keysym == 'Escape':
            if not self.game_over:
                self.paused = not self.paused
        elif event.keysym == 'F1':
            self.reset_game()
        elif not self.game_over and not self.paused:
            if event.keysym == 'Left':
                if not self.check_collision(offset_x=self.current_x - 1):
                    self.current_x -= 1
            elif event.keysym == 'Right':
                if not self.check_collision(offset_x=self.current_x + 1):
                    self.current_x += 1
            elif event.keysym == 'Down':
                if not self.check_collision(offset_y=self.current_y + 1):
                    self.current_y += 1
            elif event.keysym == 'Up':
                self.rotate_piece()
    
    def update(self):
        if not self.game_over and not self.paused:
            if not self.check_collision(offset_y=self.current_y + 1):
                self.current_y += 1
            else:
                self.lock_piece()
        
        self.draw()
        self.root.after(self.speed, self.update)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = TetrisGame()
    game.run() 