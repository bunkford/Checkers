import tkinter as tk
from tkinter import messagebox
from copy import deepcopy
import random

class CheckersGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Checkers")
        
        # Colors
        self.DARK_SQUARE = "#8B4513"  # Saddle Brown
        self.LIGHT_SQUARE = "#DEB887"  # Burlywood
        self.RED_PIECE = "#FF0000"
        self.BLACK_PIECE = "#000000"
        self.HIGHLIGHT = "#90EE90"  # Light Green
        
        # Game state
        self.board_size = 8
        self.square_size = 60
        self.piece_padding = 10
        self.selected_piece = None
        self.current_player = "RED"
        self.board = self.initialize_board()
        self.move_stack = []  # Stack to store (board, current_player, moves_since_last_capture) before each move
        self.redo_stack = []  # Stack to store (board, current_player, moves_since_last_capture) for redo functionality
        self.opponent_type = tk.StringVar(value="AI")  # Default opponent type HUMAN or AI
        self.ai_skill_level = tk.StringVar(value='Regular')  # AI Skill Level variable
        
        # Draw condition variables
        self.moves_since_last_capture = 0
        self.draw_threshold = 40  # Number of consecutive moves without capture to declare a draw
                
        # Create canvas
        canvas_size = self.board_size * self.square_size
        self.canvas = tk.Canvas(
            self.root,
            width=canvas_size,
            height=canvas_size
        )
        self.canvas.pack()
        
        # Bind click event
        self.canvas.bind('<Button-1>', self.handle_click)
        
        # Draw initial board
        self.draw_board()
        self.draw_pieces()
        
        # Add menu for opponent selection and move options
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        
        # Game menu
        self.game_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Game", menu=self.game_menu)
        self.game_menu.add_command(label="New Game", command=self.reset_game)
        self.game_menu.add_command(label="Quit", command=self.root.quit)
        
        # Opponent menu
        self.opponent_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Opponent", menu=self.opponent_menu)
        self.opponent_menu.add_radiobutton(label="Human", command=lambda: self.set_opponent_type("HUMAN"), variable=self.opponent_type, value="HUMAN")
        self.opponent_menu.add_radiobutton(label="AI", command=lambda: self.set_opponent_type("AI"), variable=self.opponent_type, value="AI")
        
        # Move menu
        self.move_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Move", menu=self.move_menu)
        self.move_menu.add_command(label="Undo", command=self.undo_move, accelerator="Ctrl+Z")
        self.move_menu.add_command(label="Redo", command=self.redo_move, accelerator="Ctrl+Y")
        
        # AI Skill Level menu
        self.skill_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="AI Skill", menu=self.skill_menu)
        self.skill_menu.add_radiobutton(label="Beginner", command=lambda: self.set_ai_skill_level("Beginner"), variable=self.ai_skill_level, value="Beginner")
        self.skill_menu.add_radiobutton(label="Regular", command=lambda: self.set_ai_skill_level("Regular"), variable=self.ai_skill_level, value="Regular")
        self.skill_menu.add_radiobutton(label="Expert", command=lambda: self.set_ai_skill_level("Expert"), variable=self.ai_skill_level, value="Expert")
        self.skill_menu.add_radiobutton(label="Master", command=lambda: self.set_ai_skill_level("Master"), variable=self.ai_skill_level, value="Master")
        
        # Bind keyboard shortcuts
        self.root.bind_all("<Control-z>", lambda event: self.undo_move())
        self.root.bind_all("<Control-y>", lambda event: self.redo_move())
    
    def set_ai_skill_level(self, level):
        self.ai_skill_level.set(level)
    
    def set_opponent_type(self, opponent_type):
        self.opponent_type.set(opponent_type)
        if opponent_type == "AI" and self.current_player == "BLACK":
            self.root.after(500, self.ai_move)
    
    def initialize_board(self):
        board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        
        # Place initial pieces
        for row in range(self.board_size):
            for col in range(self.board_size):
                if row < 3 and (row + col) % 2 == 1:
                    board[row][col] = {"color": "BLACK", "king": False}
                elif row > 4 and (row + col) % 2 == 1:
                    board[row][col] = {"color": "RED", "king": False}
                    
        return board
    
    def draw_board(self):
        self.canvas.delete("square")
        for row in range(self.board_size):
            for col in range(self.board_size):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                
                color = self.LIGHT_SQUARE if (row + col) % 2 == 0 else self.DARK_SQUARE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="", tags="square")
    
    def draw_pieces(self):
        self.canvas.delete("piece")
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece:
                    self.draw_piece(row, col, piece)
    
    def draw_piece(self, row, col, piece):
        x = col * self.square_size + self.square_size // 2
        y = row * self.square_size + self.square_size // 2
        radius = (self.square_size - 2 * self.piece_padding) // 2
        
        color = self.RED_PIECE if piece["color"] == "RED" else self.BLACK_PIECE
        
        # Draw the main piece
        self.canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=color, tags="piece"
        )
        
        # Draw king crown if piece is king
        if piece["king"]:
            crown_radius = radius * 0.6
            crown_color = "gold"
            self.canvas.create_oval(
                x - crown_radius, y - crown_radius,
                x + crown_radius, y + crown_radius,
                fill=crown_color, tags="piece"
            )
    
    def get_square_from_coords(self, x, y):
        row = y // self.square_size
        col = x // self.square_size
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return row, col
        return None
    
    def get_valid_moves(self, row, col, player_color=None):
        piece = self.board[row][col]
        if not piece:
            return [], []
        if player_color and piece["color"] != player_color:
            return [], []
        if player_color is None and piece["color"] != self.current_player:
            return [], []
        
        valid_moves = []
        jumps = []
        directions = []
        
        # Determine valid directions based on piece type and color
        if piece["color"] == "RED" and not piece["king"]:
            directions = [(-1, -1), (-1, 1)]  # Red moves up
        elif piece["color"] == "BLACK" and not piece["king"]:
            directions = [(1, -1), (1, 1)]    # Black moves down
        else:  # King can move in all directions
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            
        # Check for regular moves and jumps
        for d_row, d_col in directions:
            # Regular moves
            new_row = row + d_row
            new_col = col + d_col
            if self.is_valid_position(new_row, new_col):
                if not self.board[new_row][new_col]:
                    valid_moves.append((new_row, new_col))
                    
            # Jumps
            jump_row = row + 2 * d_row
            jump_col = col + 2 * d_col
            middle_row = row + d_row
            middle_col = col + d_col
            if (self.is_valid_position(jump_row, jump_col) and 
                self.is_valid_position(middle_row, middle_col)):
                jumped_piece = self.board[middle_row][middle_col]
                if (jumped_piece and 
                    jumped_piece["color"] != piece["color"] and 
                    not self.board[jump_row][jump_col]):
                    jumps.append((jump_row, jump_col))
        
        return jumps, valid_moves
    
    def is_valid_position(self, row, col):
        return 0 <= row < self.board_size and 0 <= col < self.board_size
    
    def highlight_valid_moves(self, moves):
        for row, col in moves:
            x1 = col * self.square_size
            y1 = row * self.square_size
            x2 = x1 + self.square_size
            y2 = y1 + self.square_size
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=self.HIGHLIGHT,
                stipple="gray50",
                tags="highlight"
            )
    
    def clear_highlights(self):
        self.canvas.delete("highlight")
    
    def handle_click(self, event):
        if self.current_player == "BLACK" and self.opponent_type.get() == "AI":
            return  # Ignore clicks during AI's turn
        
        clicked_square = self.get_square_from_coords(event.x, event.y)
        if not clicked_square:
            return
        
        row, col = clicked_square
        
        # Determine if there are any mandatory jumps for the current player
        mandatory_jumps = self.get_all_mandatory_jumps()
        if mandatory_jumps:
            # If there are mandatory jumps, only allow selecting pieces with jumps
            if not self.selected_piece:
                if (row, col) not in [pos[:2] for pos in mandatory_jumps]:
                    return
            else:
                # If a piece is selected, ensure that the move is part of the mandatory jumps
                from_row, from_col = self.selected_piece
                valid_jump_positions = [ (move[2], move[3]) for move in mandatory_jumps if move[0] == from_row and move[1] == from_col ]
                if (row, col) not in valid_jump_positions:
                    return
        
        # If no piece is selected
        if not self.selected_piece:
            piece = self.board[row][col]
            if piece and piece["color"] == self.current_player:
                self.selected_piece = (row, col)
                jumps, regular_moves = self.get_valid_moves(row, col)
                # If jumps are available, only show those
                valid_moves = jumps if jumps else regular_moves
                self.highlight_valid_moves(valid_moves)
        
        # If a piece is already selected
        else:
            selected_row, selected_col = self.selected_piece
            jumps, regular_moves = self.get_valid_moves(selected_row, selected_col)
            valid_moves = jumps if jumps else regular_moves
            
            # If jumps are available, only allow jumps
            if jumps and not self.is_jump_move(row, selected_row):
                return
            
            # If clicked square is a valid move
            if (row, col) in valid_moves:
                # Determine if this is a jump move
                is_jump = abs(row - selected_row) == 2
                
                # Save the current board state, current player, and move counter for undo functionality
                # Save BEFORE moving
                self.move_stack.append((deepcopy(self.board), self.current_player, self.moves_since_last_capture))
                self.redo_stack.clear()  # Clear the redo stack since new move is made
                
                # Move the piece
                self.move_piece(selected_row, selected_col, row, col, is_jump)
                
                # Update move counter
                if is_jump:
                    self.moves_since_last_capture = 0
                else:
                    self.moves_since_last_capture += 1
                
                # Check for draw condition
                if self.moves_since_last_capture >= self.draw_threshold:
                    messagebox.showinfo("Draw", "The game is a draw due to too many moves without capture!")
                    self.reset_game()
                    return
                
                # Check for additional jumps
                additional_jumps, _ = self.get_valid_moves(row, col)
                
                # If piece was promoted to king, update directions
                if self.board[row][col]["king"]:
                    # Recalculate jumps if promoted
                    additional_jumps, _ = self.get_valid_moves(row, col)
                
                # Only switch players if:
                # 1. It wasn't a jump move, or
                # 2. It was a jump move but there are no additional jumps available
                if not is_jump or not additional_jumps:
                    self.switch_player()
                    self.selected_piece = None

                    winner = self.check_winner()
                    if winner:
                        messagebox.showinfo("Game Over", f"{winner} wins!")
                        self.reset_game()
                        return

                    # If opponent is AI, make an automatic move
                    if self.opponent_type.get() == "AI" and self.current_player == "BLACK":
                        self.root.after(500, self.ai_move)
                else:
                    # If there are additional jumps, keep the piece selected
                    self.selected_piece = (row, col)
                    self.highlight_valid_moves(additional_jumps)
                    return
            
            self.selected_piece = None
            self.clear_highlights()
    
    def is_jump_move(self, target_row, from_row):
        return abs(target_row - from_row) == 2
    
    def get_all_mandatory_jumps(self):
        mandatory_jumps = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece and piece["color"] == self.current_player:
                    jumps, _ = self.get_valid_moves(row, col)
                    if jumps:
                        for jump in jumps:
                            mandatory_jumps.append((row, col, jump[0], jump[1]))
        return mandatory_jumps
    
    def move_piece(self, from_row, from_col, to_row, to_col, is_jump=False):
        # Move the piece
        piece = self.board[from_row][from_col]
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None

        # Remove the jumped piece if it's a jump move
        if is_jump:
            jumped_row = (from_row + to_row) // 2
            jumped_col = (from_col + to_col) // 2
            self.board[jumped_row][jumped_col] = None

        # Check for king promotion immediately
        if piece["color"] == "RED" and to_row == 0:
            piece["king"] = True
        elif piece["color"] == "BLACK" and to_row == self.board_size - 1:
            piece["king"] = True

        # Redraw the board to show the changes
        self.draw_board()
        self.draw_pieces()
    
    def switch_player(self):
        self.current_player = "BLACK" if self.current_player == "RED" else "RED"
    
    def has_valid_moves(self, player_color):
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece and piece["color"] == player_color:
                    jumps, regular_moves = self.get_valid_moves(row, col, player_color=player_color)
                    if jumps or regular_moves:
                        return True
        return False
    
    def check_winner(self):
        # Check if either player has no pieces left or no valid moves
        red_pieces = black_pieces = 0
        red_has_moves = black_has_moves = False
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece:
                    if piece["color"] == "RED":
                        red_pieces += 1
                        if not red_has_moves:
                            jumps, moves = self.get_valid_moves(row, col, player_color="RED")
                            if jumps or moves:
                                red_has_moves = True
                    else:
                        black_pieces += 1
                        if not black_has_moves:
                            jumps, moves = self.get_valid_moves(row, col, player_color="BLACK")
                            if jumps or moves:
                                black_has_moves = True
        if red_pieces == 0 or not red_has_moves:
            return "BLACK"
        elif black_pieces == 0 or not black_has_moves:
            return "RED"
        else:
            return None
    
    def reset_game(self):
        self.board = self.initialize_board()
        self.current_player = "RED"
        self.selected_piece = None
        self.move_stack = []
        self.redo_stack = []
        self.moves_since_last_capture = 0  # Reset move counter
        self.clear_highlights()
        self.draw_board()
        self.draw_pieces()
        if self.opponent_type.get() == "AI" and self.current_player == "BLACK":
            self.root.after(500, self.ai_move)
    
    def undo_move(self):
        if self.move_stack:
            # Save current state to redo stack
            self.redo_stack.append((deepcopy(self.board), self.current_player, self.moves_since_last_capture))
            # Restore previous state
            self.board, self.current_player, self.moves_since_last_capture = self.move_stack.pop()
            self.selected_piece = None
            self.clear_highlights()
            self.draw_board()
            self.draw_pieces()
            # If it's AI's turn after undo and opponent is AI, schedule AI move
            if self.opponent_type.get() == "AI" and self.current_player == "BLACK":
                self.root.after(1000, self.ai_move)
        else:
            messagebox.showwarning("Undo", "No moves to undo!")
    
    def redo_move(self):
        if self.redo_stack:
            # Save current state to move stack
            self.move_stack.append((deepcopy(self.board), self.current_player, self.moves_since_last_capture))
            # Restore next state
            self.board, self.current_player, self.moves_since_last_capture = self.redo_stack.pop()
            self.selected_piece = None
            self.clear_highlights()
            self.draw_board()
            self.draw_pieces()
            # If it's AI's turn after redo and opponent is AI, schedule AI move
            if self.opponent_type.get() == "AI" and self.current_player == "BLACK":
                self.root.after(1000, self.ai_move)
        else:
            messagebox.showwarning("Redo", "No moves to redo!")
    
    def ai_move(self):
        # Ensure it's the AI's turn
        if self.current_player != "BLACK" or self.opponent_type.get() != "AI":
            return  # It's not AI's turn

        # Determine search depth based on AI skill level
        skill_level = self.ai_skill_level.get()
        depth_mapping = {
            "Beginner": 1,
            "Regular": 3,
            "Expert": 4,
            "Master": 5
        }
        depth = depth_mapping.get(skill_level, 3)  # Default to Regular if undefined

        # Execute AI move using Minimax with the determined depth
        best_move = None
        best_score = float('-inf')
        possible_moves = self.get_all_possible_moves(self.board, self.current_player)

        if not possible_moves:
            winner = self.check_winner()
            if winner:
                messagebox.showinfo("Game Over", f"{winner} wins!")
                self.reset_game()
            return  # No valid moves available

        for move in possible_moves:
            temp_board = deepcopy(self.board)
            self.simulate_move(temp_board, *move)
            score = self.minimax(temp_board, depth - 1, float('-inf'), float('inf'), False)
            if score > best_score:
                best_score = score
                best_move = move

        if best_move is None:
            # No valid moves
            winner = self.check_winner()
            if winner:
                messagebox.showinfo("Game Over", f"{winner} wins!")
                self.reset_game()
            return

        from_row, from_col, to_row, to_col, is_jump = best_move

        # Save the current board state, current player, and move counter for undo functionality
        # Save BEFORE moving
        self.move_stack.append((deepcopy(self.board), self.current_player, self.moves_since_last_capture))
        self.redo_stack.clear()  # Clear the redo stack since a new move is made

        # Move the piece
        self.move_piece(from_row, from_col, to_row, to_col, is_jump)

        # Update move counter
        if is_jump:
            self.moves_since_last_capture = 0
        else:
            self.moves_since_last_capture += 1

        # Check for draw condition
        if self.moves_since_last_capture >= self.draw_threshold:
            messagebox.showinfo("Draw", "The game is a draw due to too many moves without capture!")
            self.reset_game()
            return

        # Check for additional jumps
        if is_jump:
            additional_jumps, _ = self.get_valid_moves(to_row, to_col)
            if additional_jumps:
                # Schedule the next jump after a delay
                self.root.after(500, lambda: self.ai_move())
                return

        # No additional jumps, end turn
        self.switch_player()
        winner = self.check_winner()
        if winner:
            messagebox.showinfo("Game Over", f"{winner} wins!")
            self.reset_game()
        elif self.opponent_type.get() == "AI" and self.current_player == "BLACK":
            self.root.after(500, self.ai_move)
    
    def get_all_possible_moves(self, board, player_color):
        """
        Collect all possible moves for the given player.
        If any jumps exist, only return jumps. Otherwise, return regular moves.
        """
        all_jumps = []
        all_regular_moves = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = board[row][col]
                if piece and piece["color"] == player_color:
                    jumps, regular_moves = self.get_valid_moves_on_board(board, row, col, player_color=player_color)
                    for jump in jumps:
                        all_jumps.append((row, col, jump[0], jump[1], True))
                    if not jumps:
                        for move in regular_moves:
                            all_regular_moves.append((row, col, move[0], move[1], False))
        if all_jumps:
            return all_jumps
        else:
            return all_regular_moves
    
    def get_valid_moves_on_board(self, board, row, col, player_color=None):
        # Similar to get_valid_moves, but operates on a given board
        piece = board[row][col]
        if not piece:
            return [], []
        if player_color and piece["color"] != player_color:
            return [], []
        if player_color is None and piece["color"] != self.current_player:
            return [], []
    
        valid_moves = []
        jumps = []
        directions = []
    
        # Determine valid directions based on piece type and color
        if piece["color"] == "RED" and not piece["king"]:
            directions = [(-1, -1), (-1, 1)]  # Red moves up
        elif piece["color"] == "BLACK" and not piece["king"]:
            directions = [(1, -1), (1, 1)]    # Black moves down
        else:  # King can move in all directions
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    
        # Check for regular moves and jumps
        for d_row, d_col in directions:
            # Regular moves
            new_row = row + d_row
            new_col = col + d_col
            if self.is_valid_position(new_row, new_col):
                if not board[new_row][new_col]:
                    valid_moves.append((new_row, new_col))
    
            # Jumps
            jump_row = row + 2 * d_row
            jump_col = col + 2 * d_col
            middle_row = row + d_row
            middle_col = col + d_col
            if (self.is_valid_position(jump_row, jump_col) and 
                self.is_valid_position(middle_row, middle_col)):
                jumped_piece = board[middle_row][middle_col]
                if (jumped_piece and 
                    jumped_piece["color"] != piece["color"] and 
                    not board[jump_row][jump_col]):
                    jumps.append((jump_row, jump_col))
    
        return jumps, valid_moves
    
    def simulate_move(self, board, from_row, from_col, to_row, to_col, is_jump=False):
        """
        Simulate moving a piece on a given board.
        """
        # Move the piece
        piece = board[from_row][from_col].copy()  # Copy the piece to avoid modifying the original
        board[to_row][to_col] = piece
        board[from_row][from_col] = None

        # Remove the jumped piece if it's a jump move
        if is_jump:
            jumped_row = (from_row + to_row) // 2
            jumped_col = (from_col + to_col) // 2
            board[jumped_row][jumped_col] = None

        # Check for king promotion immediately
        if piece["color"] == "RED" and to_row == 0:
            piece["king"] = True
        elif piece["color"] == "BLACK" and to_row == self.board_size - 1:
            piece["king"] = True
    
    def evaluate_board(self, board, player_color):
        """
        Evaluate the board from the perspective of player_color.
        Positive scores are good for player_color, negative scores are bad.
        """
        score = 0
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = board[row][col]
                if piece:
                    value = 1
                    if piece["king"]:
                        value = 1.5  # kings are more valuable
                    if piece["color"] == player_color:
                        score += value
                    else:
                        score -= value
        return score
    
    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """
        Minimax algorithm with alpha-beta pruning.
        Returns the evaluation score.
        """
        if depth == 0 or self.is_terminal_state(board):
            return self.evaluate_board(board, self.current_player)

        if maximizing_player:
            max_eval = float('-inf')
            possible_moves = self.get_all_possible_moves(board, "BLACK")
            if not possible_moves:
                return self.evaluate_board(board, self.current_player)
            for move in possible_moves:
                new_board = deepcopy(board)
                self.simulate_move(new_board, *move)
                eval = self.minimax(new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            possible_moves = self.get_all_possible_moves(board, "RED")
            if not possible_moves:
                return self.evaluate_board(board, self.current_player)
            for move in possible_moves:
                new_board = deepcopy(board)
                self.simulate_move(new_board, *move)
                eval = self.minimax(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
    
    def is_terminal_state(self, board):
        # Return True if the game is over (one player has no pieces or no moves)
        red_pieces = black_pieces = 0
        red_has_moves = black_has_moves = False
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = board[row][col]
                if piece:
                    if piece["color"] == "RED":
                        red_pieces += 1
                        if not red_has_moves:
                            jumps, moves = self.get_valid_moves_on_board(board, row, col, player_color="RED")
                            if jumps or moves:
                                red_has_moves = True
                    else:
                        black_pieces += 1
                        if not black_has_moves:
                            jumps, moves = self.get_valid_moves_on_board(board, row, col, player_color="BLACK")
                            if jumps or moves:
                                black_has_moves = True
        if red_pieces == 0 or not red_has_moves or black_pieces == 0 or not black_has_moves:
            return True
        else:
            return False
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = CheckersGame()
    game.run()
