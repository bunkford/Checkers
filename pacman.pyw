import tkinter as tk
import random
import math

class PacmanGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pac-Man")
        
        # Constants
        self.CELL_SIZE = 30
        self.GRID_WIDTH = 19
        self.GRID_HEIGHT = 21
        self.GAME_WIDTH = self.GRID_WIDTH * self.CELL_SIZE
        self.GAME_HEIGHT = self.GRID_HEIGHT * self.CELL_SIZE
        self.BASE_SPEED = 100  # Movement speed in milliseconds
        
        # Colors
        self.COLORS = {
            'wall': '#2121ff',      # Blue walls
            'dot': '#ffd700',       # Gold dots
            'power': '#fff',        # White power pellets
            'pacman': '#ffff00',    # Yellow pacman
            'blinky': '#ff0000',    # Red ghost
            'pinky': '#ffb8ff',     # Pink ghost
            'inky': '#00ffff',      # Cyan ghost
            'clyde': '#ffb852',     # Orange ghost
            'scared': '#2121ff'     # Blue scared ghosts
        }
        
        # Game state
        self.score = 0
        self.level = 1
        self.lives = 3
        self.paused = False
        self.game_over = True
        
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
        
        # Create score display
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(fill=tk.X, padx=10)
        
        self.score_label = tk.Label(
            self.info_frame,
            text=f"Score: {self.score}",
            font=("Arial", 16)
        )
        self.score_label.pack(side=tk.LEFT, padx=10)
        
        self.lives_label = tk.Label(
            self.info_frame,
            text=f"Lives: {self.lives}",
            font=("Arial", 16)
        )
        self.lives_label.pack(side=tk.RIGHT, padx=10)
        
        # Bind keys
        self.root.bind("<Key>", self.handle_keypress)
        
        # Make window non-resizable
        self.root.resizable(False, False)
        
        # Define the maze layout
        self.MAZE = [
            "WWWWWWWWWWWWWWWWWWW",
            "W........W........W",
            "WPWW.WWW.W.WWW.WWpW",
            "W.................W",
            "W.WW.W.WWWWW.W.WW.W",
            "W....W...W...W....W",
            "WWWW.WWW W WWW.WWWW",
            "   W.W   G   W.W   ",
            "WWWW.W WW-WW W.WWWW",
            "    .  WgggW  .    ",
            "WWWW.W WWWWW W.WWWW",
            "   W.W       W.W   ",
            "WWWW.W WWWWW W.WWWW",
            "W........W........W",
            "W.WW.WWW.W.WWW.WW.W",
            "Wp..W.....P.....W.W",
            "WWW.W.W.WWW.W.W.W.W",
            "W........W........W",
            "W.WWWWWW.W.WWWWWW.W",
            "W.................W",
            "WWWWWWWWWWWWWWWWWWW"
        ]
        
        self.reset_game()
        self.update()
    
    def create_menu(self):
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Game menu
        game_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game", command=self.reset_game)
        game_menu.add_separator()
        game_menu.add_command(label="Quit", command=self.root.quit)
    
    def reset_game(self):
        self.game_over = False
        self.paused = False
        self.score = 0
        self.lives = 3
        self.level = 1
        self.power_mode = False
        self.power_timer = None
        
        # Initialize game grid
        self.grid = []
        self.dots_left = 0
        
        for row in self.MAZE:
            grid_row = []
            for cell in row:
                if cell == 'W':
                    grid_row.append('wall')
                elif cell == '.':
                    self.dots_left += 1
                    grid_row.append('dot')
                elif cell == 'P':
                    grid_row.append('empty')
                    self.pacman_pos = [len(self.grid), len(grid_row)]
                    self.pacman_direction = [0, 0]
                    self.next_direction = [0, 0]
                elif cell == 'p':
                    self.dots_left += 1
                    grid_row.append('power')
                elif cell == 'G':
                    grid_row.append('empty')
                    self.ghost_start = [len(self.grid), len(grid_row)]
                else:
                    grid_row.append('empty')
            self.grid.append(grid_row)
        
        # Initialize ghosts
        self.ghosts = [
            {'pos': self.ghost_start[:], 'direction': [0, 0], 'color': 'blinky', 'mode': 'scatter'},
            {'pos': self.ghost_start[:], 'direction': [0, 0], 'color': 'pinky', 'mode': 'scatter'},
            {'pos': self.ghost_start[:], 'direction': [0, 0], 'color': 'inky', 'mode': 'scatter'},
            {'pos': self.ghost_start[:], 'direction': [0, 0], 'color': 'clyde', 'mode': 'scatter'}
        ]
        
        self.update_labels()
    
    def update_labels(self):
        self.score_label.config(text=f"Score: {self.score}")
        self.lives_label.config(text=f"Lives: {self.lives}")
    
    def handle_keypress(self, event):
        if event.keysym == 'Escape':
            if not self.game_over:
                self.paused = not self.paused
        elif event.keysym == 'F1':
            self.reset_game()
        elif not self.game_over and not self.paused:
            if event.keysym == 'Left':
                self.next_direction = [0, -1]
            elif event.keysym == 'Right':
                self.next_direction = [0, 1]
            elif event.keysym == 'Up':
                self.next_direction = [-1, 0]
            elif event.keysym == 'Down':
                self.next_direction = [1, 0]
    
    def move_pacman(self):
        # Try to move in the next_direction if it's valid
        next_pos = [
            self.pacman_pos[0] + self.next_direction[0],
            self.pacman_pos[1] + self.next_direction[1]
        ]
        
        if (0 <= next_pos[0] < self.GRID_HEIGHT and 
            0 <= next_pos[1] < self.GRID_WIDTH and 
            self.grid[next_pos[0]][next_pos[1]] != 'wall'):
            self.pacman_direction = self.next_direction[:]
        
        # Move in current direction
        next_pos = [
            self.pacman_pos[0] + self.pacman_direction[0],
            self.pacman_pos[1] + self.pacman_direction[1]
        ]
        
        if (0 <= next_pos[0] < self.GRID_HEIGHT and 
            0 <= next_pos[1] < self.GRID_WIDTH and 
            self.grid[next_pos[0]][next_pos[1]] != 'wall'):
            self.pacman_pos = next_pos
            
            # Check for dot collection
            if self.grid[next_pos[0]][next_pos[1]] == 'dot':
                self.grid[next_pos[0]][next_pos[1]] = 'empty'
                self.score += 10
                self.dots_left -= 1
            elif self.grid[next_pos[0]][next_pos[1]] == 'power':
                self.grid[next_pos[0]][next_pos[1]] = 'empty'
                self.score += 50
                self.dots_left -= 1
                self.activate_power_mode()
    
    def activate_power_mode(self):
        self.power_mode = True
        if self.power_timer:
            self.root.after_cancel(self.power_timer)
        self.power_timer = self.root.after(10000, self.end_power_mode)
        
        for ghost in self.ghosts:
            if ghost['mode'] != 'eaten':
                ghost['mode'] = 'scared'
    
    def end_power_mode(self):
        self.power_mode = False
        self.power_timer = None
        for ghost in self.ghosts:
            if ghost['mode'] == 'scared':
                ghost['mode'] = 'scatter'
    
    def move_ghosts(self):
        for ghost in self.ghosts:
            if ghost['mode'] == 'eaten':
                # Move towards ghost house
                target = self.ghost_start
            elif ghost['mode'] == 'scatter':
                # Move towards corner
                target = [0, 0]  # Simplified targeting
            else:  # chase or scared
                target = self.pacman_pos
            
            # Simple pathfinding
            possible_moves = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_pos = [ghost['pos'][0] + dx, ghost['pos'][1] + dy]
                if (0 <= new_pos[0] < self.GRID_HEIGHT and 
                    0 <= new_pos[1] < self.GRID_WIDTH and 
                    self.grid[new_pos[0]][new_pos[1]] != 'wall'):
                    if ghost['mode'] == 'scared':
                        possible_moves.append([dx, dy])
                    else:
                        dist = math.hypot(target[0] - new_pos[0], target[1] - new_pos[1])
                        possible_moves.append(([dx, dy], dist))
            
            if possible_moves:
                if ghost['mode'] == 'scared':
                    ghost['direction'] = random.choice(possible_moves)
                else:
                    ghost['direction'] = min(possible_moves, key=lambda x: x[1])[0]
                
                ghost['pos'][0] += ghost['direction'][0]
                ghost['pos'][1] += ghost['direction'][1]
    
    def check_collisions(self):
        for ghost in self.ghosts:
            if ghost['pos'] == self.pacman_pos:
                if ghost['mode'] == 'scared':
                    ghost['mode'] = 'eaten'
                    self.score += 200
                else:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self.pacman_pos = [15, 9]  # Reset position
                        self.pacman_direction = [0, 0]
                        self.next_direction = [0, 0]
    
    def draw(self):
        self.canvas.delete("all")
        
        # Draw maze
        for row in range(self.GRID_HEIGHT):
            for col in range(self.GRID_WIDTH):
                x1 = col * self.CELL_SIZE
                y1 = row * self.CELL_SIZE
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE
                
                cell = self.grid[row][col]
                if cell == 'wall':
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.COLORS['wall'], outline="")
                elif cell == 'dot':
                    self.canvas.create_oval(x1+12, y1+12, x2-12, y2-12, fill=self.COLORS['dot'])
                elif cell == 'power':
                    self.canvas.create_oval(x1+8, y1+8, x2-8, y2-8, fill=self.COLORS['power'])
        
        # Draw Pac-Man
        x1 = self.pacman_pos[1] * self.CELL_SIZE
        y1 = self.pacman_pos[0] * self.CELL_SIZE
        x2 = x1 + self.CELL_SIZE
        y2 = y1 + self.CELL_SIZE
        self.canvas.create_oval(x1+2, y1+2, x2-2, y2-2, fill=self.COLORS['pacman'])
        
        # Draw ghosts
        for ghost in self.ghosts:
            x1 = ghost['pos'][1] * self.CELL_SIZE
            y1 = ghost['pos'][0] * self.CELL_SIZE
            x2 = x1 + self.CELL_SIZE
            y2 = y1 + self.CELL_SIZE
            color = self.COLORS['scared'] if ghost['mode'] == 'scared' else self.COLORS[ghost['color']]
            self.canvas.create_oval(x1+2, y1+2, x2-2, y2-2, fill=color)
        
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
    
    def update(self):
        if not self.game_over and not self.paused:
            self.move_pacman()
            self.move_ghosts()
            self.check_collisions()
            self.update_labels()
            
            # Check for level completion
            if self.dots_left == 0:
                self.level += 1
                self.reset_game()
        
        self.draw()
        self.root.after(self.BASE_SPEED, self.update)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = PacmanGame()
    game.run() 