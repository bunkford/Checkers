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
        self.BASE_SPEED = 250  # Slower speed (was 100)
        self.GHOST_JAIL_TIME = 5000  # Time in ms that ghosts stay in jail
        self.GHOST_RELEASE_DELAY = 2000  # Time between releasing each ghost
        self.jailed_ghosts = {}  # Track jailed ghosts and their release timers
        self.POWER_DURATION = 10000  # 10 seconds total
        self.BLINK_START = 7000      # Start blinking after 7 seconds
        self.BLINK_SPEED = 200       # Blink every 200ms
        self.power_time = 0          # Track how long power mode has been active
        self.blink_state = False     # Track blink state
        self.ghost_release_queue = []  # Queue for ghosts waiting to be released
        
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
        
        # Define the maze layout with proper ghost house and exit
        self.MAZE = [
            "WWWWWWWWWWWWWWWWWWW",
            "W........W........W",
            "WPWW.WWW.W.WWW.WWpW",
            "W.................W",
            "W.WW.W.WWWWW.W.WW.W",
            "W....W...W...W....W",
            "WWWW.WWW W WWW.WWWW",
            "   W.W       W.W   ",
            "WWWW.W WWWWW W.WWWW",
            "    .  WgggW  .    ",
            "WWWW.W WgGgW W.WWWW",
            "   W.W WgggW W.W   ",
            "WWWW.W W   W W.WWWW",  # Changed: Clear path in middle
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
        # Cancel any existing jail timers
        for timer_id in self.jailed_ghosts.values():
            self.root.after_cancel(timer_id)
        self.jailed_ghosts = {}
        
        self.game_over = False
        self.paused = False
        self.score = 0
        self.lives = 3
        self.level = 1
        self.power_mode = False
        self.power_timer = None
        self.power_time = 0
        self.blink_state = False
        
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
                    grid_row.append('ghost_house')
                    self.ghost_start = [len(self.grid), len(grid_row)]
                elif cell == 'g':
                    grid_row.append('ghost_house')
                elif cell == 'd':
                    grid_row.append('door')  # New cell type for doorway
                else:
                    grid_row.append('empty')
            self.grid.append(grid_row)
        
        # Initialize ghosts with better starting positions inside ghost house
        self.ghosts = [
            {'pos': [self.ghost_start[0], self.ghost_start[1]-1], 'direction': [0, 0], 'color': 'blinky', 'mode': 'house'},
            {'pos': [self.ghost_start[0], self.ghost_start[1]+1], 'direction': [0, 0], 'color': 'pinky', 'mode': 'house'},
            {'pos': [self.ghost_start[0]-1, self.ghost_start[1]], 'direction': [0, 0], 'color': 'inky', 'mode': 'house'},
            {'pos': [self.ghost_start[0]+1, self.ghost_start[1]], 'direction': [0, 0], 'color': 'clyde', 'mode': 'house'}
        ]
        
        # Set up release sequence
        self.ghost_release_queue = self.ghosts.copy()
        self.root.after(self.GHOST_RELEASE_DELAY, self.release_next_ghost)
        
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
        
        # Check for tunnel first
        next_pos = self.handle_tunnel(next_pos)
        
        if (0 <= next_pos[0] < self.GRID_HEIGHT and 
            0 <= next_pos[1] < self.GRID_WIDTH and 
            self.grid[next_pos[0]][next_pos[1]] != 'wall'):
            self.pacman_direction = self.next_direction[:]
        
        # Move in current direction
        next_pos = [
            self.pacman_pos[0] + self.pacman_direction[0],
            self.pacman_pos[1] + self.pacman_direction[1]
        ]
        
        # Check for tunnel again
        next_pos = self.handle_tunnel(next_pos)
        
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
        self.power_time = 0  # Reset power time
        self.blink_state = False
        
        if self.power_timer:
            self.root.after_cancel(self.power_timer)
        self.power_timer = self.root.after(self.POWER_DURATION, self.end_power_mode)
        
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
            if ghost['mode'] == 'jailed':
                # Keep ghost in jail
                ghost['pos'] = [self.ghost_start[0], self.ghost_start[1]]
                ghost['direction'] = [0, 0]
                continue
            
            if ghost['mode'] == 'house':
                # Move to exit position when in house mode
                exit_pos = [self.ghost_start[0] - 2, self.ghost_start[1]]  # Position above ghost house
                
                # First move to center if not there
                if ghost['pos'][1] != self.ghost_start[1]:
                    if ghost['pos'][1] < self.ghost_start[1]:
                        ghost['pos'][1] += 1
                    else:
                        ghost['pos'][1] -= 1
                # Then move up
                elif ghost['pos'][0] > exit_pos[0]:
                    ghost['pos'][0] -= 1
                else:
                    ghost['mode'] = 'scatter'  # Switch to scatter mode once at exit
                continue
            
            # If ghost is in ghost house area but not in house mode, move upward to exit
            if self.grid[ghost['pos'][0]][ghost['pos'][1]] == 'ghost_house':
                next_pos = [ghost['pos'][0] - 1, ghost['pos'][1]]
                if self.is_valid_move(next_pos):
                    ghost['pos'] = next_pos
                    ghost['direction'] = [-1, 0]
                    continue
            
            if ghost['direction'] == [0, 0]:
                # Ghost needs a new direction
                possible_moves = self.get_possible_moves(ghost['pos'])
                if possible_moves:
                    ghost['direction'] = random.choice(possible_moves)
            else:
                # Continue in current direction until hitting a wall
                next_pos = [
                    ghost['pos'][0] + ghost['direction'][0],
                    ghost['pos'][1] + ghost['direction'][1]
                ]
                
                # Handle tunnel movement for ghosts
                next_pos = self.handle_tunnel(next_pos)
                
                # Check if next position is valid
                if self.is_valid_move(next_pos):
                    ghost['pos'] = next_pos
                    
                    # Check if at intersection
                    possible_moves = self.get_possible_moves(ghost['pos'])
                    if len(possible_moves) > 2:  # More than 2 options means it's an intersection
                        # 30% chance to change direction at intersection
                        if random.random() < 0.3:
                            # Remove opposite of current direction to prevent reversing
                            opposite = [-ghost['direction'][0], -ghost['direction'][1]]
                            possible_moves.remove(opposite) if opposite in possible_moves else None
                            ghost['direction'] = random.choice(possible_moves)
                else:
                    # Hit a wall, choose new direction
                    possible_moves = self.get_possible_moves(ghost['pos'])
                    if possible_moves:
                        # Remove opposite of current direction to prevent reversing
                        opposite = [-ghost['direction'][0], -ghost['direction'][1]]
                        possible_moves.remove(opposite) if opposite in possible_moves else None
                        ghost['direction'] = random.choice(possible_moves) if possible_moves else [0, 0]
    
    def get_possible_moves(self, pos):
        possible_moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_pos = [pos[0] + dx, pos[1] + dy]
            if self.is_valid_move(new_pos):
                possible_moves.append([dx, dy])
        return possible_moves
    
    def is_valid_move(self, pos):
        # Handle tunnel positions
        if pos[0] == 9:  # Tunnel row
            if pos[1] < 0 or pos[1] >= self.GRID_WIDTH:  # In tunnel
                return True
        
        if (0 <= pos[0] < self.GRID_HEIGHT and 
            0 <= pos[1] < self.GRID_WIDTH):
            cell = self.grid[pos[0]][pos[1]]
            # Ghosts can move through doors and ghost house, Pac-Man cannot
            if cell == 'ghost_house' or cell == 'door':
                return isinstance(self, dict)  # True for ghosts (passed as dict), False for Pac-Man
            return cell != 'wall'
        return False
    
    def check_collisions(self):
        for ghost in self.ghosts:
            if ghost['pos'] == self.pacman_pos:
                if ghost['mode'] == 'scared':
                    ghost['mode'] = 'eaten'
                    self.score += 200
                    # Send ghost to jail
                    ghost['pos'] = self.ghost_start[:]
                    self.jail_ghost(ghost)
                elif ghost['mode'] != 'jailed':  # Don't collide while in jail
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
                elif cell == 'door':
                    # Draw doorway as a thin line
                    self.canvas.create_line(x1, y1, x2, y1, fill=self.COLORS['wall'], width=2)
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
            x = ghost['pos'][1] * self.CELL_SIZE
            y = ghost['pos'][0] * self.CELL_SIZE
            
            # Determine ghost color based on mode and blink state
            if ghost['mode'] == 'scared':
                if self.power_time >= self.BLINK_START:
                    # Blink between scared and normal color
                    color = self.COLORS[ghost['color']] if self.blink_state else self.COLORS['scared']
                else:
                    color = self.COLORS['scared']
            else:
                color = self.COLORS[ghost['color']]
            
            # Draw ghost body (slightly taller than cell)
            self.canvas.create_arc(
                x + 2, y + 2,
                x + self.CELL_SIZE - 2, y + self.CELL_SIZE - 2,
                start=0, extent=180,
                fill=color
            )
            self.canvas.create_rectangle(
                x + 2, y + self.CELL_SIZE//2,
                x + self.CELL_SIZE - 2, y + self.CELL_SIZE - 2,
                fill=color, outline=color
            )
            
            # Draw wavy bottom
            wave_points = [
                x + 2,                    y + self.CELL_SIZE - 2,  # Start
                x + self.CELL_SIZE//4,    y + self.CELL_SIZE - 8,  # First valley
                x + self.CELL_SIZE//2,    y + self.CELL_SIZE - 2,  # Middle peak
                x + 3*self.CELL_SIZE//4,  y + self.CELL_SIZE - 8,  # Second valley
                x + self.CELL_SIZE - 2,   y + self.CELL_SIZE - 2   # End
            ]
            self.canvas.create_line(wave_points, fill=color, width=2, smooth=True)
            
            # Draw eyes
            eye_color = "white" if ghost['mode'] != 'scared' else self.COLORS['scared']
            pupil_color = "blue" if ghost['mode'] == 'scared' else "black"
            
            # Left eye
            self.canvas.create_oval(
                x + 7, y + 8,
                x + 13, y + 14,
                fill=eye_color, outline=eye_color
            )
            self.canvas.create_oval(
                x + 9, y + 9,
                x + 12, y + 12,
                fill=pupil_color
            )
            
            # Right eye
            self.canvas.create_oval(
                x + 17, y + 8,
                x + 23, y + 14,
                fill=eye_color, outline=eye_color
            )
            self.canvas.create_oval(
                x + 19, y + 9,
                x + 22, y + 12,
                fill=pupil_color
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
    
    def update(self):
        if not self.game_over and not self.paused:
            self.move_pacman()
            self.move_ghosts()
            self.check_collisions()
            self.update_labels()
            
            # Update power mode timing and blinking
            if self.power_mode:
                self.power_time += self.BASE_SPEED
                if self.power_time >= self.BLINK_START:
                    # Toggle blink state
                    if self.power_time % self.BLINK_SPEED < self.BASE_SPEED:
                        self.blink_state = not self.blink_state
            
            # Check for level completion
            if self.dots_left == 0:
                self.level += 1
                self.reset_game()
        
        self.draw()
        self.root.after(self.BASE_SPEED, self.update)
    
    def run(self):
        self.root.mainloop()
    
    def jail_ghost(self, ghost):
        ghost['mode'] = 'house'  # Change to house mode instead of jailed
        ghost['pos'] = [self.ghost_start[0], self.ghost_start[1]]  # Place in center
        timer_id = self.root.after(self.GHOST_JAIL_TIME, lambda: self.release_ghost(ghost))
        self.jailed_ghosts[ghost['color']] = timer_id
    
    def release_ghost(self, ghost):
        if ghost['color'] in self.jailed_ghosts:
            del self.jailed_ghosts[ghost['color']]
        ghost['mode'] = 'house'  # Set to house mode to trigger exit behavior
    
    def handle_tunnel(self, pos):
        # Check for tunnel positions (row 9 in the maze)
        if pos[0] == 9:  # Tunnel row
            if pos[1] < 0:  # Left tunnel
                return [pos[0], self.GRID_WIDTH - 1]
            elif pos[1] >= self.GRID_WIDTH:  # Right tunnel
                return [pos[0], 0]
        return pos
    
    def release_next_ghost(self):
        if self.ghost_release_queue and not self.game_over and not self.paused:
            ghost = self.ghost_release_queue.pop(0)
            ghost['mode'] = 'scatter'
            # Schedule next ghost release
            if self.ghost_release_queue:
                self.root.after(self.GHOST_RELEASE_DELAY, self.release_next_ghost)

if __name__ == "__main__":
    game = PacmanGame()
    game.run() 