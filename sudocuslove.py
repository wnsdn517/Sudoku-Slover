# pip install customtkinter
import customtkinter as tk
from tkinter import messagebox, filedialog, Entry
import time
import os
import re

class Sudoku:
    def __init__(self, master):
        self.master = master
        self.master.title("9x9 Sudoku Solver")
        self.board = [[None for _ in range(9)] for _ in range(9)]
        self.current_cell = (0, 0)
        self.start_time = None
        self.elapsed_time = 0
        self.solved = 0
        self.board_frame = tk.CTkFrame(self.master)
        self.board_frame.pack(padx=10, pady=10)
        for i in range(9):
            for j in range(9):
                padx = 1
                pady = 1 
                if i % 3 == 0 and i != 0:
                    pady += 2
                if j % 3 == 0 and j != 0:
                    padx += 2
                entry = Entry(self.board_frame, font=('Helvetica', 20, 'bold'), width=2, justify='center')
                entry.grid(row=i, column=j, padx=(padx, 1), pady=(pady, 1))
                entry.bind('<Up>', self.move_up)
                entry.bind('<Down>', self.move_down)
                entry.bind('<Left>', self.move_left)
                entry.bind('<Right>', self.move_right)
                entry.bind('<Return>', self.move_next)
                entry.bind('<Key>', self.limit_input_length)
                entry.bind('<BackSpace>', self.clear_entry)
                entry.bind('<Button-1>', self.select_cell)
                self.board[i][j] = entry

        self.btnframe = tk.CTkFrame(self.master)
        self.btnframe.pack()
        self.solve_button = tk.CTkButton(self.btnframe, text="Solve", font=('Helvetica', 16), command=self.solve_puzzle)
        self.solve_button.pack(padx=(0, 10), side="left")

        self.reset_button = tk.CTkButton(self.btnframe, text="Clear All", font=('Helvetica', 16), command=self.reset_puzzle)
        self.reset_button.pack(side="right")

        self.time_label = tk.CTkLabel(self.master, text="Elapse: 0s", font=('Helvetica', 16))
        self.time_label.pack(pady=10)

    def limit_input_length(self, event):
        entry = event.widget
        char = event.char
        if char == '\x08':
            entry.delete(len(entry.get()) - 1)
            return "break"
        if not re.match(r'^\d$', char):
            return "break"
        if len(entry.get()) >= 1:
            return "break"
        if char == "0":
            return "break"

    def clear_entry(self, event):
        entry = event.widget
        entry.delete(0, tk.END)

    def solve_puzzle(self):
        self.start_time = time.time()
        puzzle = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                value = self.board[i][j].get()
                if value.isdigit():
                    puzzle[i][j] = int(value)
                    if len(value) == 1:
                        self.board[i][j].configure(state='disabled')

        if self.solve_sudoku(puzzle):
            self.show_solution(puzzle)
        else:
            self.show_unsolvable_message()

    def show_solution(self, puzzle):
        self.solved = 1
        self.highlight_3x3_area()
        for i in range(9):
            for j in range(9):
                self.board[i][j].delete(0, tk.END)
                self.board[i][j].insert(0, str(puzzle[i][j]))
                self.board[i][j].configure(font=('Helvetica', 20))
        self.elapsed_time = round(time.time() - self.start_time, 2)
        self.time_label.configure(text=f"Elapse: {self.elapsed_time}s")
        self.solve_button.configure(text="Save", command=lambda: self.save_result(puzzle))
        self.reset_button.configure(text="Reset")

    def show_unsolvable_message(self):
        messagebox.showwarning("Warning", "Unsolvable puzzle.")
        self.reset_button.configure(state=tk.NORMAL)

        for i in range(9):
            for j in range(9):
                self.board[i][j].configure(state='normal')

    def reset_puzzle(self):
        self.start_time = None
        self.elapsed_time = 0
        self.solved = 0
        self.time_label.configure(text="Elapse: 0s")
        self.solve_button.configure(text="Solve", command=self.solve_puzzle)
        self.reset_button.configure(text="Clear All")
        for i in range(9):
            for j in range(9):
                self.board[i][j].delete(0, tk.END)
                self.board[i][j].configure(state='normal', font=('Helvetica', 20))
                self.board[i][j].delete(0, tk.END)

    def solve_sudoku(self, puzzle):
        empty_cell = self.find_empty_cell(puzzle)
        if not empty_cell:
            return True

        row, col = empty_cell
        for num in range(1, 10):
            if self.is_valid_move(puzzle, row, col, num):
                puzzle[row][col] = num
                if self.solve_sudoku(puzzle):
                    return True
                puzzle[row][col] = 0

        return False

    def find_empty_cell(self, puzzle):
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] == 0:
                    return (i, j)
        return None

    def is_valid_move(self, puzzle, row, col, num):
        return self.is_valid_row(puzzle, row, num) and self.is_valid_column(puzzle, col, num) and self.is_valid_box(
            puzzle, row, col, num)

    def is_valid_row(self, puzzle, row, num):
        return num not in puzzle[row]

    def is_valid_column(self, puzzle, col, num):
        for i in range(9):
            if puzzle[i][col] == num:
                return False
        return True

    def is_valid_box(self, puzzle, row, col, num):
        start_row = row - row % 3
        start_col = col - col % 3
        for i in range(3):
            for j in range(3):
                if puzzle[start_row + i][start_col + j] == num:
                    return False
        return True

    def select_cell(self, event):
        entry = event.widget
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == entry:
                    self.current_cell = (i, j)
                    self.update_cell_focus()
                    self.highlight_3x3_area()

    def update_cell_focus(self):
        row, col = self.current_cell
        self.board[row][col].focus_set()
        for i in range(9):
            for j in range(9):
                if i == row and j == col:
                    self.board[i][j].configure(font=('Helvetica', 20, 'bold'))
                else:
                    self.board[i][j].configure(font=('Helvetica', 20))

    def highlight_3x3_area(self):
        self.clear_highlight()
        row, col = self.current_cell
        for i in range(9):
            for j in range(9):
                if i // 3 == row // 3 and j // 3 == col // 3 or i // 1 == row // 1 or j // 1 == col // 1:
                    if self.solved == 0:
                        self.board[i][j].configure(bg='#F5F6CE')

    def clear_highlight(self):
        for i in range(9):
            for j in range(9):
                self.board[i][j].configure(bg='#FFFFFF')

    def move(self, event, row_change=0, col_change=0):
        row, col = self.current_cell
        new_row, new_col = row + row_change, col + col_change

        if 0 <= new_row <= 8 and 0 <= new_col <= 8:
            self.board[row][col].configure(font=('Helvetica', 20))
            self.current_cell = (new_row, new_col)
            self.board[new_row][new_col].focus_set()
            self.board[new_row][new_col].configure(font=('Helvetica', 20, 'bold'))
            self.highlight_3x3_area()

    def move_up(self, event):
        self.move(event, row_change=-1)

    def move_down(self, event):
        self.move(event, row_change=1)

    def move_left(self, event):
        self.move(event, col_change=-1)

    def move_right(self, event):
        self.move(event, col_change=1)

    def move_next(self, event):
        row, col = self.current_cell
        self.move(event, row_change=1, col_change=-col) if col == 8 else self.move(event, col_change=1)

    def save_result(self, puzzle):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("text file", "*.txt")], title="Save As..")
        if file_path:
            if os.path.exists(file_path):
                overwrite = messagebox.askyesno("Warning", "File already exists. Overwrite?")
                if not overwrite:
                    return
            with open(file_path, 'w') as file:
                for row in puzzle:
                    file.write(' '.join(map(str, row)) + '\n')

root = tk.CTk()
game = Sudoku(root)
root.mainloop()
