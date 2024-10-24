import tkinter as tk
import random

class BackgammonGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Backgammon")
        
        # Constants
        self.BOARD_WIDTH = 800
        self.BOARD_HEIGHT = 600
        self.POINT_WIDTH = 40
        self.CHECKER_RADIUS = 15
        self.POINT_HEIGHT = 200
        self.MIDDLE_BAR_WIDTH = 30  # Increased from 20
        self.MIDDLE_BAR_PADDING = 20  # Added padding for middle bar
        
        # Game state
        self.board = self.initialize_board()
        self.current_player = None  # Will be set after determining who goes first
        self.selected_point = None
        self.dice = []
        self.moves_remaining = []
        self.bar = {1: 0, -1: 0}  # Pieces on the bar for each player
        self.bear_off = {1: 0, -1: 0}  # Pieces borne off for each player
        
        # Valid end points and their move sequences
        self.valid_end_points = {}
        
        # Piece IDs for animation
        self.piece_ids = {}  # Maps positions to lists of canvas item IDs
        
        # Opponent settings
        self.opponent_type = 'AI'  # Default to AI
        self.ai_skill_level = 'Beginner'  # Default to Beginner
        
        # Create menu
        self.create_menu()
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.BOARD_WIDTH,
            height=self.BOARD_HEIGHT,
            bg='burlywood3'
        )
        self.canvas.pack(pady=10)
        
        # Create status bar
        self.status_bar = tk.Label(self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind click events
        self.canvas.bind('<Button-1>', self.handle_click)
        
        # Draw initial board
        self.draw_board()
        
        # Determine who goes first
        self.determine_first_player()
        
        # Variable to store roll button ID
        self.roll_button_id = None
        
        # Animation variables
        self.animating = False
        
    def create_menu(self):
        self.menubar = tk.Menu(self.root)
        
        # Game menu
        game_menu = tk.Menu(self.menubar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.new_game)
        game_menu.add_command(label="Quit", command=self.root.quit)
        self.menubar.add_cascade(label="Game", menu=game_menu)
        
        # Opponent menu
        self.opponent_menu = tk.Menu(self.menubar, tearoff=0)
        self.opponent_var = tk.StringVar(value=self.opponent_type)
        self.opponent_menu.add_radiobutton(label="Human", variable=self.opponent_var,
                                           command=lambda: self.set_opponent('Human'))
        self.opponent_menu.add_radiobutton(label="AI", variable=self.opponent_var,
                                           command=lambda: self.set_opponent('AI'))
        self.menubar.add_cascade(label="Opponent", menu=self.opponent_menu)
        
        # AI Skill Level menu
        self.ai_menu = tk.Menu(self.menubar, tearoff=0)
        self.ai_skill_var = tk.StringVar(value=self.ai_skill_level)
        self.ai_menu.add_radiobutton(label="Beginner", variable=self.ai_skill_var,
                                     command=lambda: self.set_ai_skill('Beginner'))
        self.ai_menu.add_radiobutton(label="Intermediate", variable=self.ai_skill_var,
                                     command=lambda: self.set_ai_skill('Intermediate'))
        self.ai_menu.add_radiobutton(label="Advanced", variable=self.ai_skill_var,
                                     command=lambda: self.set_ai_skill('Advanced'))
        self.menubar.add_cascade(label="AI Skill Level", menu=self.ai_menu)
        
        self.root.config(menu=self.menubar)
        
    def set_opponent(self, opponent_type):
        self.opponent_type = opponent_type
        self.opponent_var.set(opponent_type)
        self.status_bar.config(text=f"Opponent set to {opponent_type}")
        
    def set_ai_skill(self, skill_level):
        self.ai_skill_level = skill_level
        self.ai_skill_var.set(skill_level)
        self.status_bar.config(text=f"AI skill level set to {skill_level}")
        
    def initialize_board(self):
        board = [0] * 24
        # White pieces
        board[0] = 2   # 2 pieces on point 1
        board[11] = 5  # 5 pieces on point 12
        board[16] = 3  # 3 pieces on point 17
        board[18] = 5  # 5 pieces on point 19
        
        # Black pieces
        board[23] = -2  # 2 pieces on point 24
        board[12] = -5  # 5 pieces on point 13
        board[7] = -3   # 3 pieces on point 8
        board[5] = -5   # 5 pieces on point 6
        
        return board
        
    def new_game(self):
        # Reset the game state
        self.board = self.initialize_board()
        self.current_player = None
        self.selected_point = None
        self.dice = []
        self.moves_remaining = []
        self.bar = {1: 0, -1: 0}
        self.bear_off = {1: 0, -1: 0}
        self.valid_end_points = {}
        self.roll_button_id = None
        self.draw_board()
        self.determine_first_player()
        
    def determine_first_player(self):
        while True:
            player1_roll = random.randint(1, 6)
            player2_roll = random.randint(1, 6)
            self.dice = [player1_roll, player2_roll]
            self.moves_remaining = self.dice.copy()
            self.draw_board()
            self.root.update()  # Update the window to show the dice
            if player1_roll > player2_roll:
                self.current_player = 1
                self.status_bar.config(text=f"White goes first with rolls {player1_roll} and {player2_roll}.")
                break
            elif player2_roll > player1_roll:
                self.current_player = -1
                self.status_bar.config(text=f"Black goes first with rolls {player2_roll} and {player1_roll}.")
                break
            else:
                # Tie, roll again
                self.status_bar.config(text=f"Both players rolled {player1_roll}. Rolling again.")
                self.root.after(1000)
                continue
            
        # Check if AI needs to make the first move
        if self.current_player == -1 and self.opponent_type == 'AI':
            self.roll_dice()  # Roll dice automatically for AI
            self.root.after(500, self.ai_move)
        else:
            self.draw_roll_button()
            
    def draw_board(self):
        self.canvas.delete("all")
        self.piece_ids = {}  # Reset piece IDs
        
        # Draw middle bar
        bar_x = self.BOARD_WIDTH / 2
        self.canvas.create_rectangle(
            bar_x - self.MIDDLE_BAR_WIDTH/2, 50,
            bar_x + self.MIDDLE_BAR_WIDTH/2, self.BOARD_HEIGHT - 50,
            fill='burlywood4'
        )
        
        # Draw points
        for i in range(24):
            x = self.get_point_x(i)
            y = 50 if i < 12 else self.BOARD_HEIGHT - 50
            color = 'brown' if (i % 2 == 0) else 'grey'
            
            # Draw triangle
            if i < 12:
                # Top side
                self.canvas.create_polygon(
                    x, y,
                    x + self.POINT_WIDTH, y,
                    x + self.POINT_WIDTH/2, y + self.POINT_HEIGHT,
                    fill=color
                )
            else:
                # Bottom side
                self.canvas.create_polygon(
                    x, y,
                    x + self.POINT_WIDTH, y,
                    x + self.POINT_WIDTH/2, y - self.POINT_HEIGHT,
                    fill=color
                )
        
        # Draw border around bearing off areas
        # White bearing off area (right side)
        x1 = self.BOARD_WIDTH - 70
        y1 = 50
        x2 = self.BOARD_WIDTH - 30
        y2 = self.BOARD_HEIGHT - 50
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline='blue',
            width=2
        )
        # Black bearing off area (left side)
        x1 = 30
        y1 = 50
        x2 = 70
        y2 = self.BOARD_HEIGHT - 50
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline='blue',
            width=2
        )
        
        # Draw pieces
        for i in range(24):
            pieces = self.board[i]
            if pieces != 0:
                self.draw_pieces(i, pieces)
        
        # Draw bar pieces
        self.draw_bar_pieces()
        
        # Draw borne off pieces
        self.draw_bear_off_pieces()
        
        # Highlight selected point
        if self.selected_point is not None:
            self.highlight_selected_point(self.selected_point)
            self.highlight_valid_moves(self.selected_point)
        
        # Draw dice
        self.draw_dice()
        
        # Draw roll dice button if needed
        if self.current_player == 1 and not self.moves_remaining:
            self.draw_roll_button()
        
    def draw_roll_button(self):
        # Remove existing roll button if any
        if hasattr(self, 'roll_button_id') and hasattr(self, 'roll_button_text'):
            self.canvas.delete(self.roll_button_id)
            self.canvas.delete(self.roll_button_text)
            self.roll_button_id = None
            self.roll_button_text = None
        
        # Draw a rectangle as a button
        x1 = self.BOARD_WIDTH / 2 - 50
        y1 = self.BOARD_HEIGHT - 70
        x2 = x1 + 100
        y2 = y1 + 40
        self.roll_button_id = self.canvas.create_rectangle(
            x1, y1, x2, y2, fill='lightgray', outline='black'
        )
        self.roll_button_text = self.canvas.create_text(
            (x1 + x2) / 2, (y1 + y2) / 2,
            text="Roll Dice", font=("Arial", 14)
        )
        
        self.canvas.tag_bind(self.roll_button_id, '<Button-1>', self.roll_dice)
        self.canvas.tag_bind(self.roll_button_text, '<Button-1>', self.roll_dice)
        
    def get_point_x(self, point):
        board_middle = self.BOARD_WIDTH / 2
        total_padding = self.MIDDLE_BAR_WIDTH + (self.MIDDLE_BAR_PADDING * 2)
        
        if point < 6:  # Top right quadrant
            return board_middle + total_padding/2 + (5 - point) * self.POINT_WIDTH
        elif point < 12:  # Top left quadrant
            return board_middle - total_padding/2 - self.POINT_WIDTH * 6 + (11 - point) * self.POINT_WIDTH
        elif point < 18:  # Bottom left quadrant
            return board_middle - total_padding/2 - self.POINT_WIDTH * 6 + (point - 12) * self.POINT_WIDTH
        else:  # Bottom right quadrant
            return board_middle + total_padding/2 + (point - 18) * self.POINT_WIDTH
    
    def draw_pieces(self, point, count):
        x = self.get_point_x(point) + self.POINT_WIDTH/2
        abs_count = abs(count)
        color = 'white' if count > 0 else 'black'
        self.piece_ids[point] = []
        
        for i in range(abs_count):
            if point < 12:
                # Top side
                y = 70 + (i * 1.8 * (self.CHECKER_RADIUS + 4))
            else:
                # Bottom side
                y = self.BOARD_HEIGHT - 70 - (i * 1.8 * (self.CHECKER_RADIUS + 4))
            
            piece_id = self.canvas.create_oval(
                x - self.CHECKER_RADIUS,
                y - self.CHECKER_RADIUS,
                x + self.CHECKER_RADIUS,
                y + self.CHECKER_RADIUS,
                fill=color,
                outline='gray'
            )
            self.piece_ids[point].append(piece_id)
    
    def draw_bar_pieces(self):
        x = self.BOARD_WIDTH / 2
        y_white = self.BOARD_HEIGHT / 2 + 50
        y_black = self.BOARD_HEIGHT / 2 - 50
        # Draw white pieces on the bar
        self.piece_ids['bar_w'] = []
        for i in range(self.bar[1]):
            y = y_white + (i * 1.8 * (self.CHECKER_RADIUS + 4))
            piece_id = self.canvas.create_oval(
                x - self.CHECKER_RADIUS,
                y - self.CHECKER_RADIUS,
                x + self.CHECKER_RADIUS,
                y + self.CHECKER_RADIUS,
                fill='white',
                outline='gray'
            )
            self.piece_ids['bar_w'].append(piece_id)
        # Draw black pieces on the bar
        self.piece_ids['bar_b'] = []
        for i in range(self.bar[-1]):
            y = y_black - (i * 1.8 * (self.CHECKER_RADIUS + 4))
            piece_id = self.canvas.create_oval(
                x - self.CHECKER_RADIUS,
                y - self.CHECKER_RADIUS,
                x + self.CHECKER_RADIUS,
                y + self.CHECKER_RADIUS,
                fill='black',
                outline='gray'
            )
            self.piece_ids['bar_b'].append(piece_id)
    
    def draw_bear_off_pieces(self):
        # Draw borne off pieces for white (right side)
        x_white = self.BOARD_WIDTH - 50
        y_white = self.BOARD_HEIGHT / 2 + 50
        self.piece_ids['off_w'] = []
        for i in range(self.bear_off[1]):
            y = y_white + (i * 1.8 * (self.CHECKER_RADIUS + 4))
            piece_id = self.canvas.create_oval(
                x_white - self.CHECKER_RADIUS,
                y - self.CHECKER_RADIUS,
                x_white + self.CHECKER_RADIUS,
                y + self.CHECKER_RADIUS,
                fill='white',
                outline='gray'
            )
            self.piece_ids['off_w'].append(piece_id)
        # Draw borne off pieces for black (left side)
        x_black = 50
        y_black = self.BOARD_HEIGHT / 2 - 50
        self.piece_ids['off_b'] = []
        for i in range(self.bear_off[-1]):
            y = y_black - (i * 1.8 * (self.CHECKER_RADIUS + 4))
            piece_id = self.canvas.create_oval(
                x_black - self.CHECKER_RADIUS,
                y - self.CHECKER_RADIUS,
                x_black + self.CHECKER_RADIUS,
                y + self.CHECKER_RADIUS,
                fill='black',
                outline='gray'
            )
            self.piece_ids['off_b'].append(piece_id)
    
    def draw_dice(self):
        if not self.dice:  # If dice haven't been rolled yet, don't draw
            return
        
        # Adjusted size and position
        dice_size = 40
        dice_padding = 10
        dice_to_draw = self.moves_remaining  # Show only remaining moves
    
        total_dice_width = len(dice_to_draw) * (dice_size + dice_padding) - dice_padding
        x = (self.BOARD_WIDTH - total_dice_width) / 2
        y = self.BOARD_HEIGHT - dice_size - 80  # Adjusted position
    
        for die in dice_to_draw:
            # Draw dice outline
            self.canvas.create_rectangle(x, y, x + dice_size, y + dice_size, fill="white")
            # Draw dots for the current die
            self.draw_dice_dots(x, y, die, dice_size)
            x += dice_size + dice_padding
    
    def draw_dice_dots(self, x, y, value, dice_size):
        dot_radius = dice_size * 0.08  # Adjust dot size relative to dice size
        center = dice_size / 2
        offset = dice_size * 0.25
        positions = {
            1: [(x + center, y + center)],
            2: [(x + offset, y + offset), (x + dice_size - offset, y + dice_size - offset)],
            3: [(x + offset, y + offset), (x + center, y + center), (x + dice_size - offset, y + dice_size - offset)],
            4: [(x + offset, y + offset), (x + dice_size - offset, y + offset), (x + offset, y + dice_size - offset), (x + dice_size - offset, y + dice_size - offset)],
            5: [(x + offset, y + offset), (x + dice_size - offset, y + offset), (x + offset, y + dice_size - offset), (x + dice_size - offset, y + dice_size - offset), (x + center, y + center)],
            6: [(x + offset, y + offset), (x + offset, y + center), (x + offset, y + dice_size - offset), (x + dice_size - offset, y + offset), (x + dice_size - offset, y + center), (x + dice_size - offset, y + dice_size - offset)]
        }
    
        for position in positions[value]:
            self.canvas.create_oval(
                position[0] - dot_radius, position[1] - dot_radius,
                position[0] + dot_radius, position[1] + dot_radius,
                fill="black"
            )
        
    def roll_dice(self, event=None):
        if not self.moves_remaining:
            self.dice = [random.randint(1, 6), random.randint(1, 6)]
            self.moves_remaining = self.dice.copy()
            if self.dice[0] == self.dice[1]:
                self.moves_remaining *= 2
            self.draw_board()
            # Remove roll button after rolling
            if self.roll_button_id:
                self.canvas.delete(self.roll_button_id)
                self.canvas.delete(self.roll_button_text)
                self.roll_button_id = None
                self.roll_button_text = None
            # Check if player has any valid moves
            has_moves = self.generate_all_possible_moves_player()
            if not has_moves:
                self.status_bar.config(text="No available moves. Turn skipped.")
                self.end_turn()
            else:
                self.status_bar.config(text=f"Rolled dice: {self.dice}")
        
    def handle_click(self, event):
        if self.animating:
            return  # Ignore clicks during animation
        if self.opponent_type == 'AI' and self.current_player == -1:
            return  # Ignore clicks when it's AI's turn

        if not self.moves_remaining:
            return
                    
        x = event.x
        y = event.y
        
        # Calculate which point was clicked
        clicked_point = None
        
        # Check if clicking on the bar
        if self.bar[self.current_player] > 0:
            # Player must move from the bar
            if self.is_click_on_bar(x, y):
                clicked_point = 'bar'
            else:
                # Check if clicking on valid move from bar
                for point in self.valid_end_points:
                    point_x = self.get_point_x(point)
                    if point_x <= x <= point_x + self.POINT_WIDTH:
                        clicked_point = point
                        break
        else:
            for i in range(24):
                point_x = self.get_point_x(i)
                if point_x <= x <= point_x + self.POINT_WIDTH:
                    if i < 12:
                        # Top side
                        if y <= self.BOARD_HEIGHT / 2:
                            clicked_point = i
                    else:
                        # Bottom side
                        if y >= self.BOARD_HEIGHT / 2:
                            clicked_point = i
        
        # Check if clicking on roll button
        if self.roll_button_id:
            x1 = self.BOARD_WIDTH / 2 - 50
            y1 = self.BOARD_HEIGHT - 70
            x2 = x1 + 100
            y2 = y1 + 40
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.roll_dice()
                return
    
        if clicked_point is not None:
            if self.selected_point is None:
                # Check if point has current player's pieces
                if clicked_point == 'bar':
                    if self.bar[self.current_player] > 0:
                        self.selected_point = 'bar'
                        self.draw_board()
                        self.highlight_valid_moves('bar')
                elif (self.board[clicked_point] * self.current_player) > 0:
                    self.selected_point = clicked_point
                    self.draw_board()
                    self.highlight_valid_moves(clicked_point)
            else:
                # If clicking on the same point, deselect it
                if clicked_point == self.selected_point:
                    self.selected_point = None
                    self.valid_end_points = {}
                    self.draw_board()
                    return
                
                # Try to move piece
                if clicked_point in self.valid_end_points or (clicked_point == 'bear_off' and 'bear_off' in self.valid_end_points):
                    if clicked_point == 'bear_off':
                        move_sequence = self.valid_end_points['bear_off']
                        to_point = 'bear_off'
                    else:
                        move_sequence = self.valid_end_points[clicked_point]
                        to_point = clicked_point
                    self.make_move_sequence(self.selected_point, to_point, move_sequence)
                    self.selected_point = None
                    self.valid_end_points = {}
                else:
                    # If clicking on another point with own pieces, select that instead
                    if clicked_point == 'bar':
                        if self.bar[self.current_player] > 0:
                            self.selected_point = 'bar'
                            self.draw_board()
                            self.highlight_valid_moves('bar')
                    elif (self.board[clicked_point] * self.current_player) > 0:
                        self.selected_point = clicked_point
                        self.draw_board()
                        self.highlight_valid_moves(clicked_point)
        
    def end_turn(self):
        self.current_player *= -1
        # Remove roll button if any
        if self.roll_button_id:
            self.canvas.delete(self.roll_button_id)
            self.canvas.delete(self.roll_button_text)
            self.roll_button_id = None
            self.roll_button_text = None
        if self.current_player == -1 and self.opponent_type == 'AI':
            self.roll_dice()  # Roll dice automatically for AI
            self.root.after(500, self.ai_move)
        else:
            self.draw_roll_button()
            self.status_bar.config(text="Your turn. Click 'Roll Dice' to begin.")
        
    def is_click_on_bar(self, x, y):
        bar_x1 = self.BOARD_WIDTH / 2 - self.MIDDLE_BAR_WIDTH / 2
        bar_x2 = self.BOARD_WIDTH / 2 + self.MIDDLE_BAR_WIDTH / 2
        if bar_x1 <= x <= bar_x2:
            return True
        return False
        
    def highlight_selected_point(self, point):
        if point == 'bar':
            x = self.BOARD_WIDTH / 2 - self.MIDDLE_BAR_WIDTH / 2
            y1 = 50
            y2 = self.BOARD_HEIGHT - 50
            self.canvas.create_rectangle(
                x, y1,
                x + self.MIDDLE_BAR_WIDTH, y2,
                outline='yellow',
                width=2
            )
        else:
            x = self.get_point_x(point)
            y = 50 if point < 12 else self.BOARD_HEIGHT - 50
            # Draw a highlighted triangle around the point with correct orientation
            if point < 12:
                # Top points: triangle points downwards
                self.canvas.create_polygon(
                    x, y,
                    x + self.POINT_WIDTH, y,
                    x + self.POINT_WIDTH / 2, y + self.POINT_HEIGHT,
                    outline='yellow',
                    width=2,
                    fill=''
                )
            else:
                # Bottom points: triangle points upwards
                self.canvas.create_polygon(
                    x, y,
                    x + self.POINT_WIDTH, y,
                    x + self.POINT_WIDTH / 2, y - self.POINT_HEIGHT,
                    outline='yellow',
                    width=2,
                    fill=''
                )
        
    def highlight_valid_moves(self, point):
        self.valid_end_points = self.get_valid_end_points(point, self.moves_remaining)
        for target_point in self.valid_end_points:
            if target_point == 'bear_off':
                self.highlight_bear_off_area()
            else:
                self.highlight_target_point(target_point, 'green')
        
    def highlight_bear_off_area(self):
        # Highlight the bear off area
        if self.current_player == 1:
            x1 = self.BOARD_WIDTH - 70
            y1 = 50
            x2 = self.BOARD_WIDTH - 30
            y2 = self.BOARD_HEIGHT - 50
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline='green',
                width=2
            )
        else:
            x1 = 30
            y1 = 50
            x2 = 70
            y2 = self.BOARD_HEIGHT - 50
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline='green',
                width=2
            )
        
    def highlight_target_point(self, point, color):
        x = self.get_point_x(point)
        y = 50 if point < 12 else self.BOARD_HEIGHT - 50
        # Highlight only the triangle
        if point < 12:
            self.canvas.create_polygon(
                x, y,
                x + self.POINT_WIDTH, y,
                x + self.POINT_WIDTH/2, y + self.POINT_HEIGHT,
                outline=color,
                width=2,
                fill=''
            )
        else:
            self.canvas.create_polygon(
                x, y,
                x + self.POINT_WIDTH, y,
                x + self.POINT_WIDTH/2, y - self.POINT_HEIGHT,
                outline=color,
                width=2,
                fill=''
            )
        
    def get_valid_end_points(self, start_point, moves_remaining):
        valid_end_points = {}
        moves_list = moves_remaining.copy()
        
        def recursive_moves(current_point, moves_left, used_moves):
            if not moves_left:
                return
            for i, move in enumerate(moves_left):
                if current_point == 'bar':
                    if self.current_player == 1:
                        to_point = move - 1
                    else:
                        to_point = 24 - move
                else:
                    from_point = current_point
                    if self.current_player == 1:
                        to_point = from_point + move
                    else:
                        to_point = from_point - move
                
                if to_point < 0 or to_point > 23:
                    # Check for bearing off
                    if self.can_bear_off() and self.is_bearing_off(current_point, to_point):
                        if 'bear_off' not in valid_end_points or len(used_moves + [move]) < len(valid_end_points['bear_off']):
                            valid_end_points['bear_off'] = used_moves + [move]
                    continue
                if self.board[to_point] * self.current_player < -1:
                    continue
                if self.bar[self.current_player] > 0 and current_point != 'bar':
                    continue  # Must move from bar first
                # Valid move
                if to_point not in valid_end_points or len(used_moves + [move]) < len(valid_end_points[to_point]):
                    valid_end_points[to_point] = used_moves + [move]
                # Continue moving this piece with remaining dice
                next_moves_left = moves_left[:i] + moves_left[i+1:]
                recursive_moves(to_point, next_moves_left, used_moves + [move])
        
        recursive_moves(start_point, moves_list, [])
        return valid_end_points
        
    def can_bear_off(self):
        # Check if all pieces are in the home board
        if self.current_player == 1:
            home_board = range(0, 6)
        else:
            home_board = range(18, 24)
        for i in range(24):
            if self.board[i] * self.current_player > 0 and i not in home_board:
                return False
        return True
        
    def is_bearing_off(self, from_point, to_point):
        # Check if moving off the board from home board
        if self.current_player == 1:
            return from_point >= 0 and from_point <= 5 and to_point == 24
        else:
            return from_point >= 18 and from_point <= 23 and to_point == -1
        
    def make_move_sequence(self, from_point, to_point, move_sequence):
        current_point = from_point
        moves = list(move_sequence)  # Copy the move sequence

        def move_next():
            nonlocal current_point  # Declare as nonlocal to modify the outer variable
            if not moves:
                self.selected_point = None
                self.valid_end_points = {}
                if not self.moves_remaining:
                    self.dice = []
                    self.draw_board()
                    self.end_turn()
                else:
                    if self.current_player == -1 and self.opponent_type == 'AI':
                        self.root.after(500, self.ai_move)
                return
            move = moves.pop(0)
            self.make_single_move(current_point, move, callback=move_next)
            if current_point != 'bear_off':
                current_point = self.get_new_point(current_point, move)
            else:
                current_point = 'bear_off'

        move_next()
        
    def get_new_point(self, current_point, move):
        if current_point == 'bar':
            if self.current_player == 1:
                return move - 1
            else:
                return 24 - move
        else:
            if self.current_player == 1:
                return current_point + move
            else:
                return current_point - move
        
    def make_single_move(self, from_point, distance, callback=None):
        if from_point == 'bar':
            if self.current_player == 1:
                from_pos = 'bar_w'
                to_pos = distance - 1
            else:
                from_pos = 'bar_b'
                to_pos = 24 - distance
        else:
            from_pos = from_point
            if self.current_player == 1:
                to_pos = from_pos + distance
            else:
                to_pos = from_pos - distance
        if to_pos < 0 or to_pos > 23:
            to_pos = 'off_w' if self.current_player == 1 else 'off_b'
        # Check if the move will hit an opponent's piece
        opponent_piece_id = None
        opponent_bar_pos = None
        if to_pos not in ['off_w', 'off_b']:
            if self.board[to_pos] * self.current_player == -1:
                # There is an opponent's piece to be hit
                opponent_piece_id = self.piece_ids[to_pos][-1]  # Get the opponent's piece id
                opponent_bar_pos = 'bar_w' if self.current_player == -1 else 'bar_b'
                self.piece_ids[to_pos].pop()
        # Remove the player's piece from its current position
        if from_pos in self.piece_ids and self.piece_ids[from_pos]:
            piece = self.piece_ids[from_pos].pop()
        else:
            piece = None  # Should not happen

        # Animate the move
        def after_animation():
            # After animation, update game state
            self.make_move(from_point, to_pos, distance)
            if callback:
                callback()
        self.animate_move(from_pos, to_pos, piece, opponent_piece_id, opponent_bar_pos, after_animation)
        
    def animate_move(self, from_point, to_point, piece, opponent_piece_id=None, opponent_bar_pos=None, callback=None):
        # Determine start and end positions for the player's piece
        if from_point == 'bar_w':
            x_start = self.BOARD_WIDTH / 2
            y_start = self.BOARD_HEIGHT / 2 + 50 + (len(self.piece_ids['bar_w'])) * 1.8 * (self.CHECKER_RADIUS + 4)
        elif from_point == 'bar_b':
            x_start = self.BOARD_WIDTH / 2
            y_start = self.BOARD_HEIGHT / 2 - 50 - (len(self.piece_ids['bar_b'])) * 1.8 * (self.CHECKER_RADIUS + 4)
        else:
            x_start = self.get_point_x(from_point) + self.POINT_WIDTH / 2
            stack_height = len(self.piece_ids[from_point]) + 1  # +1 because we've already popped the piece
            if from_point < 12:
                y_start = 70 + (stack_height - 1) * 1.8 * (self.CHECKER_RADIUS + 4)
            else:
                y_start = self.BOARD_HEIGHT - 70 - (stack_height - 1) * 1.8 * (self.CHECKER_RADIUS + 4)
    
        if to_point == 'off_w':
            x_end = self.BOARD_WIDTH - 50
            y_end = self.BOARD_HEIGHT / 2 + 50 + len(self.piece_ids.get('off_w', [])) * 1.8 * (self.CHECKER_RADIUS + 4)
        elif to_point == 'off_b':
            x_end = 50
            y_end = self.BOARD_HEIGHT / 2 - 50 - len(self.piece_ids.get('off_b', [])) * 1.8 * (self.CHECKER_RADIUS + 4)
        elif to_point == 'bar_w':
            x_end = self.BOARD_WIDTH / 2
            y_end = self.BOARD_HEIGHT / 2 + 50 + (len(self.piece_ids.get('bar_w', []))) * 1.8 * (self.CHECKER_RADIUS + 4)
        elif to_point == 'bar_b':
            x_end = self.BOARD_WIDTH / 2
            y_end = self.BOARD_HEIGHT / 2 - 50 - (len(self.piece_ids.get('bar_b', []))) * 1.8 * (self.CHECKER_RADIUS + 4)
        else:
            x_end = self.get_point_x(to_point) + self.POINT_WIDTH / 2
            stack_height = len(self.piece_ids.get(to_point, []))
            if to_point < 12:
                y_end = 70 + stack_height * 1.8 * (self.CHECKER_RADIUS + 4)
            else:
                y_end = self.BOARD_HEIGHT - 70 - stack_height * 1.8 * (self.CHECKER_RADIUS + 4)
    
        dx = (x_end - x_start) / 20
        dy = (y_end - y_start) / 20
        steps = 20
        self.animating = True

        def animate_player_piece(step):
            if step > steps:
                self.animating = False
                # Update piece IDs
                if to_point not in self.piece_ids:
                    self.piece_ids[to_point] = []
                self.piece_ids[to_point].append(piece)
                if callback:
                    callback()
                return
            self.canvas.move(piece, dx, dy)
            self.canvas.after(20, lambda: animate_player_piece(step + 1))

        if opponent_piece_id:
            # Animate opponent's piece to the bar
            x_opponent_start = x_end
            y_opponent_start = y_end
            x_bar = self.BOARD_WIDTH / 2
            if opponent_bar_pos == 'bar_w':
                y_bar = self.BOARD_HEIGHT / 2 + 50 + len(self.piece_ids.get('bar_w', [])) * 1.8 * (self.CHECKER_RADIUS + 4)
            else:
                y_bar = self.BOARD_HEIGHT / 2 - 50 - len(self.piece_ids.get('bar_b', [])) * 1.8 * (self.CHECKER_RADIUS + 4)
            dx_opponent = (x_bar - x_opponent_start) / 20
            dy_opponent = (y_bar - y_opponent_start) / 20

            def move_opponent_piece(step):
                if step > steps:
                    # After moving opponent's piece, update piece IDs
                    if opponent_bar_pos not in self.piece_ids:
                        self.piece_ids[opponent_bar_pos] = []
                    self.piece_ids[opponent_bar_pos].append(opponent_piece_id)
                    animate_player_piece(1)
                    return
                self.canvas.move(opponent_piece_id, dx_opponent, dy_opponent)
                self.canvas.after(20, lambda: move_opponent_piece(step + 1))

            move_opponent_piece(1)
        else:
            animate_player_piece(1)
        
    def make_move(self, from_point, to_point, distance):
        if from_point == 'bar':
            if self.current_player == 1:
                from_pos = 'bar_w'
            else:
                from_pos = 'bar_b'
        else:
            from_pos = from_point

        if to_point == 'off_w' or to_point == 'off_b':
            # Remove piece from board
            if from_pos != 'bar_w' and from_pos != 'bar_b':
                self.board[from_pos] -= self.current_player
            else:
                self.bar[self.current_player] -= 1
            self.bear_off[self.current_player] += 1
            # Remove used die
            if distance in self.moves_remaining:
                self.moves_remaining.remove(distance)
            else:
                # Remove highest die
                self.moves_remaining.remove(max(self.moves_remaining))
            # Check for win
            if self.bear_off[self.current_player] == 15:
                self.game_over()
            return

        # Move piece
        if to_point not in ['bar_w', 'bar_b']:
            if self.board[to_point] * self.current_player == -1:
                # Send opponent's piece to bar
                # Remove opponent's piece from board
                self.board[to_point] = 0  # Remove opponent's piece from board
                self.bar[-self.current_player] += 1
            self.board[to_point] += self.current_player

        if from_pos != 'bar_w' and from_pos != 'bar_b':
            self.board[from_pos] -= self.current_player
        else:
            self.bar[self.current_player] -= 1

        self.moves_remaining.remove(distance)

        # Check for win
        if self.bear_off[self.current_player] == 15:
            self.game_over()
        
    def game_over(self):
        winner = 'White' if self.current_player == 1 else 'Black'
        self.status_bar.config(text=f"{winner} wins!")
        self.root.after(5000, self.root.destroy)
        
    def ai_move(self):
        if self.animating:
            self.root.after(100, self.ai_move)
            return
        if not self.moves_remaining:
            self.dice = []
            self.draw_board()
            self.end_turn()
            return
        # Generate all possible moves for AI
        all_moves = self.generate_all_possible_moves()
        if not all_moves:
            # No available moves, skip turn
            self.status_bar.config(text="AI has no available moves and skips the turn.")
            self.end_turn()
            return
        # Choose move based on skill level
        if self.ai_skill_level == 'Beginner':
            # Random move
            move = random.choice(all_moves)
        elif self.ai_skill_level == 'Intermediate':
            # Prefer moves that hit opponent's blot
            moves_with_hits = [m for m in all_moves if m['hits_opponent']]
            if moves_with_hits:
                move = random.choice(moves_with_hits)
            else:
                move = random.choice(all_moves)
        elif self.ai_skill_level == 'Advanced':
            # Implement a simple heuristic
            move = self.select_best_move(all_moves)
        
        # Execute the move with animation
        self.selected_point = move['from_point']
        self.status_bar.config(text="AI is making a move...")
        self.make_move_sequence(move['from_point'], move['to_point'], move['move_sequence'])
        self.selected_point = None
        self.valid_end_points = {}
    
    def generate_all_possible_moves(self):
        possible_moves = []
        # Iterate over all points with AI's pieces
        starting_points = []
        if self.bar[self.current_player] > 0:
            starting_points = ['bar']
        else:
            starting_points = [i for i in range(24) if self.board[i] * self.current_player > 0]
        
        for start_point in starting_points:
            valid_end_points = self.get_valid_end_points(start_point, self.moves_remaining)
            for end_point, move_sequence in valid_end_points.items():
                hits_opponent = False
                if end_point != 'bear_off' and self.board[end_point] * self.current_player == -1:
                    hits_opponent = True
                possible_moves.append({
                    'from_point': start_point,
                    'to_point': end_point,
                    'move_sequence': move_sequence,
                    'hits_opponent': hits_opponent
                })
        return possible_moves
        
    def generate_all_possible_moves_player(self):
        # Check if player has any valid moves
        starting_points = []
        if self.bar[self.current_player] > 0:
            starting_points = ['bar']
        else:
            starting_points = [i for i in range(24) if self.board[i] * self.current_player > 0]
        
        for start_point in starting_points:
            valid_end_points = self.get_valid_end_points(start_point, self.moves_remaining)
            if valid_end_points:
                return True  # There are valid moves
        return False  # No valid moves
        
    def select_best_move(self, moves):
        # Simple heuristic: prioritize bearing off, then hitting opponent, then advancing pieces
        bearing_off_moves = [m for m in moves if m['to_point'] == 'bear_off']
        if bearing_off_moves:
            return random.choice(bearing_off_moves)
        hit_moves = [m for m in moves if m['hits_opponent']]
        if hit_moves:
            return random.choice(hit_moves)
        # Otherwise, choose the move that advances the furthest
        if self.current_player == -1:
            moves.sort(key=lambda m: m['from_point'] - (m['to_point'] if m['to_point'] != 'bear_off' else 0))
        else:
            moves.sort(key=lambda m: (m['to_point'] if m['to_point'] != 'bear_off' else 23) - m['from_point'], reverse=True)
        return moves[0]
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = BackgammonGame()
    game.run()
