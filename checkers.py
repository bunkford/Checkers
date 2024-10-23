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
        self.move_stack = []  # Stack to store (board, current_player) before each move
        self.redo_stack = []  # Stack to store (board, current_player) for redo functionality
        self.opponent_type = tk.StringVar(value="AI")  # Default opponent type HUMAN or AI
                 
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
        
        # Bind keyboard shortcuts
        self.root.bind_all("<Control-z>", lambda event: self.undo_move())
        self.root.bind_all("<Control-y>", lambda event: self.redo_move())
    
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
            new_row = row + d_row
            new_col = col + d_col
            if (self.is_valid_position(jump_row, jump_col) and 
                self.is_valid_position(new_row, new_col)):
                jumped_piece = self.board[new_row][new_col]
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
            # Ensure that if a jump is available, only jumps are allowed
            elif (row, col) not in [pos[2:] for pos in mandatory_jumps if pos[:2] == self.selected_piece]:
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
            
            # Ensure that if a jump is available, only jumps are allowed
            if jumps and (row, col) not in jumps:
                return
            
            # If clicked square is a valid move
            if (row, col) in valid_moves:
                # Determine if this is a jump move
                is_jump = abs(row - selected_row) == 2
                
                # Save the current board state and current player for undo functionality
                # Save BEFORE moving
                self.move_stack.append((deepcopy(self.board), self.current_player))
                self.redo_stack.clear()  # Clear the redo stack since new move is made
                
                # Move the piece
                self.move_piece(selected_row, selected_col, row, col, is_jump)
                
                # Check for additional jumps
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
        self.clear_highlights()
        self.draw_board()
        self.draw_pieces()
        if self.opponent_type.get() == "AI" and self.current_player == "BLACK":
            self.root.after(500, self.ai_move)
    
    def undo_move(self):
        if self.move_stack:
            # Save current state to redo stack
            self.redo_stack.append((deepcopy(self.board), self.current_player))
            # Restore previous state
            self.board, self.current_player = self.move_stack.pop()
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
            self.move_stack.append((deepcopy(self.board), self.current_player))
            # Restore next state
            self.board, self.current_player = self.redo_stack.pop()
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
        if self.current_player == "BLACK" and self.opponent_type.get() == "AI":
            # Start the AI's turn
            self.ai_make_move()
    
    def ai_make_move(self, from_row=None, from_col=None):
        # Ensure it's the AI's turn
        if self.current_player != "BLACK" or self.opponent_type.get() != "AI":
            return  # It's not AI's turn

        if from_row is not None and from_col is not None:
            # Continuing a jump sequence
            jumps, _ = self.get_valid_moves(from_row, from_col)
            if jumps:
                move = random.choice([(from_row, from_col, j[0], j[1]) for j in jumps])
            else:
                # No more jumps, end turn
                self.switch_player()
                winner = self.check_winner()
                if winner:
                    messagebox.showinfo("Game Over", f"{winner} wins!")
                    self.reset_game()
                elif self.opponent_type.get() == "AI" and self.current_player == "BLACK":
                    self.root.after(500, self.ai_move)
                return
        else:
            # First move in AI's turn
            all_jumps = []
            all_moves = []
            for row in range(self.board_size):
                for col in range(self.board_size):
                    piece = self.board[row][col]
                    if piece and piece["color"] == self.current_player:
                        jumps, regular_moves = self.get_valid_moves(row, col)
                        if jumps:
                            all_jumps.extend([(row, col, j[0], j[1]) for j in jumps])
                        elif not all_jumps:  # Only add regular moves if no jumps are available
                            all_moves.extend([(row, col, m[0], m[1]) for m in regular_moves])
            if all_jumps:
                move = random.choice(all_jumps)
            elif all_moves:
                move = random.choice(all_moves)
            else:
                winner = self.check_winner()
                if winner:
                    messagebox.showinfo("Game Over", f"{winner} wins!")
                    self.reset_game()
                return  # No valid moves available

        # Determine if this is a jump move
        from_row, from_col, to_row, to_col = move
        is_jump = abs(to_row - from_row) == 2

        # Save the current board state and current player for undo functionality
        # Save BEFORE moving
        self.move_stack.append((deepcopy(self.board), self.current_player))
        self.redo_stack.clear()  # Clear the redo stack since a new move is made

        # Move the piece
        self.move_piece(from_row, from_col, to_row, to_col, is_jump)

        # Update the UI
        self.root.update_idletasks()

        # Check for additional jumps
        if is_jump:
            additional_jumps, _ = self.get_valid_moves(to_row, to_col)
            if additional_jumps:
                # Schedule the next jump after a delay
                self.root.after(500, lambda: self.ai_make_move(to_row, to_col))
                return

        # No additional jumps, end turn
        self.switch_player()
        winner = self.check_winner()
        if winner:
            messagebox.showinfo("Game Over", f"{winner} wins!")
            self.reset_game()
        elif self.opponent_type.get() == "AI" and self.current_player == "BLACK":
            self.root.after(500, self.ai_move)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = CheckersGame()
    game.run()
