import tkinter as tk
import random

class SnakeGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Snake Game")
        
        # Constants
        self.GAME_WIDTH = 600
        self.GAME_HEIGHT = 400
        self.CELL_SIZE = 20
        self.BASE_SPEED = 200  # Base speed (level 1)
        self.level = 1
        self.paused = False
        
        # Calculate speed based on level
        self.SPEED = self.BASE_SPEED - (self.level - 1) * 15
        
        # Game state
        self.snake = [(5, 5), (4, 5), (3, 5)]  # Head is first element
        self.direction = "Right"
        self.next_direction = "Right"  # Buffer for next direction
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = True  # Start with game over state
        
        # Add blue food properties
        self.blue_food = None
        self.blue_food_timer = None
        self.BLUE_FOOD_DURATION = 3000  # Duration in milliseconds (3 seconds)
        self.BLUE_FOOD_CHANCE = 0.02    # 2% chance per update to spawn blue food
        
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
        
        # Bind keys to root window
        self.root.bind("<Key>", self.handle_keypress)  # Single key handler
        
        # Make window non-resizable
        self.root.resizable(False, False)
        
        # Bind focus events
        self.root.bind("<FocusOut>", lambda e: self.set_pause(True))
        self.root.bind("<FocusIn>", lambda e: self.set_pause(False))
        
        # Start update loop
        self.update()
    
    def create_menu(self):
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Game menu
        game_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game", command=lambda: self.reset_game(None))
        game_menu.add_separator()
        game_menu.add_command(label="Quit", command=self.root.quit)
        
        # Level menu
        self.level_menu = tk.Menu(self.menubar, tearoff=0)  # Make it instance variable
        self.menubar.add_cascade(label="Level", menu=self.level_menu)
        for i in range(1, 11):
            self.level_menu.add_command(
                label=f"Level {i}", 
                command=lambda x=i: self.set_level(x)
            )
    
    def set_level(self, level):
        if self.game_over:  # Only allow level change when game is over
            self.level = level
            self.SPEED = self.BASE_SPEED - (level - 1) * 15
            self.level_label.config(text=f"Level: {self.level}")
        else:
            print("Cannot change level during gameplay")  # Debug print
    
    def toggle_pause(self, event=None):
        if not self.game_over:  # Only allow pause if game is running
            self.paused = not self.paused
            print(f"Game {'paused' if self.paused else 'resumed'}")  # Debug print
            self.draw()  # Force redraw to show/hide pause message
    
    def set_pause(self, pause_state):
        if not self.game_over:  # Only pause if game is not over
            self.paused = pause_state
            print(f"Game {'auto-paused' if self.paused else 'auto-resumed'}")  # Debug print
            self.draw()  # Force redraw
    
    def draw_pause(self):
        self.canvas.create_text(
            self.GAME_WIDTH // 2,
            self.GAME_HEIGHT // 2,
            text="PAUSED\nPress ESC to continue",
            fill="white",
            font=("Arial", 24),
            justify="center"
        )
    
    def spawn_food(self):
        while True:
            x = random.randint(0, (self.GAME_WIDTH - self.CELL_SIZE) // self.CELL_SIZE)
            y = random.randint(0, (self.GAME_HEIGHT - self.CELL_SIZE) // self.CELL_SIZE)
            if (x, y) not in self.snake:
                return (x, y)
    
    def change_direction(self, new_direction):
        opposites = {
            "Left": "Right",
            "Right": "Left",
            "Up": "Down",
            "Down": "Up"
        }
        if opposites[new_direction] != self.direction:
            self.next_direction = new_direction
    
    def spawn_blue_food(self):
        if self.blue_food is None and not self.game_over and not self.paused:
            # Only spawn if there isn't already blue food and game is running
            if random.random() < self.BLUE_FOOD_CHANCE:
                while True:
                    x = random.randint(0, (self.GAME_WIDTH - self.CELL_SIZE) // self.CELL_SIZE)
                    y = random.randint(0, (self.GAME_HEIGHT - self.CELL_SIZE) // self.CELL_SIZE)
                    if (x, y) not in self.snake and (x, y) != self.food:
                        self.blue_food = (x, y)
                        # Set timer to remove blue food
                        if self.blue_food_timer:
                            self.root.after_cancel(self.blue_food_timer)
                        self.blue_food_timer = self.root.after(
                            self.BLUE_FOOD_DURATION, 
                            self.remove_blue_food
                        )
                        break

    def remove_blue_food(self):
        self.blue_food = None
        self.blue_food_timer = None

    def move_snake(self):
        if self.paused:
            return
            
        head = self.snake[0]
        self.direction = self.next_direction
        
        # Calculate new head position
        if self.direction == "Left":
            new_head = (head[0] - 1, head[1])
        elif self.direction == "Right":
            new_head = (head[0] + 1, head[1])
        elif self.direction == "Up":
            new_head = (head[0], head[1] - 1)
        else:  # Down
            new_head = (head[0], head[1] + 1)
        
        # Check for collisions
        if (new_head[0] < 0 or 
            new_head[0] >= self.GAME_WIDTH // self.CELL_SIZE or
            new_head[1] < 0 or 
            new_head[1] >= self.GAME_HEIGHT // self.CELL_SIZE or
            new_head in self.snake):
            self.game_over = True
            # Enable level menu when game ends
            self.set_level_menu_state('normal')
            return
        
        # Add new head
        self.snake.insert(0, new_head)
        
        growth = 0
        # Check if food was eaten
        if new_head == self.food:
            growth = 1
            self.score += 10
            self.score_label.config(text=f"Score: {self.score}")
            self.food = self.spawn_food()
        elif new_head == self.blue_food:
            growth = 5
            self.score += 50
            self.score_label.config(text=f"Score: {self.score}")
            self.remove_blue_food()
        
        if growth:
            # Grow the snake by the specified amount
            for _ in range(growth - 1):  # -1 because we already added the head
                self.snake.append(self.snake[-1])
            # Speed up the game slightly
            self.SPEED = max(50, self.SPEED - 1)
        else:
            # Remove tail if no food was eaten
            self.snake.pop()
    
    def draw(self):
        self.canvas.delete("all")
        
        # Draw snake
        for segment in self.snake:
            x1 = segment[0] * self.CELL_SIZE
            y1 = segment[1] * self.CELL_SIZE
            x2 = x1 + self.CELL_SIZE
            y2 = y1 + self.CELL_SIZE
            
            color = "white" if segment == self.snake[0] else "green2"
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
        
        # Draw regular food
        food_x1 = self.food[0] * self.CELL_SIZE
        food_y1 = self.food[1] * self.CELL_SIZE
        food_x2 = food_x1 + self.CELL_SIZE
        food_y2 = food_y1 + self.CELL_SIZE
        self.canvas.create_oval(food_x1, food_y1, food_x2, food_y2, fill="red", outline="")
        
        # Draw blue food if it exists
        if self.blue_food:
            blue_x1 = self.blue_food[0] * self.CELL_SIZE
            blue_y1 = self.blue_food[1] * self.CELL_SIZE
            blue_x2 = blue_x1 + self.CELL_SIZE
            blue_y2 = blue_y1 + self.CELL_SIZE
            self.canvas.create_oval(
                blue_x1, blue_y1, blue_x2, blue_y2,
                fill="light blue",
                outline="white"
            )
        
        # Draw game over or pause text
        if self.game_over:
            self.canvas.create_text(
                self.GAME_WIDTH // 2,
                self.GAME_HEIGHT // 2,
                text="Start new game?\n\nPress F1",
                fill="white",
                font=("Arial", 24),
                justify="center"
            )
        elif self.paused:
            self.draw_pause()
    
    def reset_game(self, event=None):
        if self.game_over or event is None:  # Allow reset from menu even if not game over
            self.snake = [(5, 5), (4, 5), (3, 5)]
            self.direction = "Right"
            self.next_direction = "Right"
            self.food = self.spawn_food()
            self.score = 0
            self.score_label.config(text="Score: 0")
            self.game_over = False
            self.paused = False
            # Keep current level and speed
            self.blue_food = None
            if self.blue_food_timer:
                self.root.after_cancel(self.blue_food_timer)
            self.blue_food_timer = None
            # Disable level menu when starting game
            self.set_level_menu_state('disabled')
    
    def update(self):
        if not self.game_over and not self.paused:
            self.move_snake()
            self.spawn_blue_food()  # Chance to spawn blue food each update
        self.draw()
        self.root.after(self.SPEED, self.update)
    
    def run(self):
        self.root.mainloop()
    
    def handle_keypress(self, event):
    
        if event.keysym == 'Escape':
            self.toggle_pause(event)
        elif event.keysym == 'F1':
            self.reset_game(event)
        elif event.keysym in ['Left', 'Right', 'Up', 'Down']:
            self.change_direction(event.keysym)
    
    def set_level_menu_state(self, state):
        """Helper method to set the state of all level menu items"""
        for i in range(self.level_menu.index('end') + 1):
            self.level_menu.entryconfigure(i, state=state)

if __name__ == "__main__":
    game = SnakeGame()
    game.run() 