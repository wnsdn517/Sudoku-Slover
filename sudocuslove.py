# pip install customtkinter
import customtkinter as tk
from hPyT import *
from CTkMenuBar import *
from CTkToolTip import *
from CTkMessagebox import *
from tkinter import filedialog, Entry,Menu,PhotoImage,Tk,Label
import time
import threading
import os
class Sudoku:
    def __init__(self, master):
        #variable
        self.board = [[None for _ in range(9)] for _ in range(9)]
        self.current_cell = (0, 0)
        self.start_time = None
        self.elapsed_time = 0
        self.solved = 0
        self.history_list = []
        self.history_file_path = "sudoku_history.txt"

        #Main GUI
        self.master = master
        self.master.withdraw()
        self.master.title("A∐Ͳʘ SUDOKU SOLVER")
        self.master.iconbitmap("SUDOKU.ico")
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW",self.exitQuestion)
        maximize_minimize_button.hide(master)

        #main frame
        self.mainframe = tk.CTkFrame(self.master)
        self.board_frame = tk.CTkFrame(self.mainframe)
        self.btnframe = tk.CTkFrame(self.mainframe)
        self.time_label = tk.CTkLabel(self.mainframe, text="Elapse: 0s", font=('Helvetica', 16))
        self.solve_button = tk.CTkButton(self.btnframe, text="Solve", font=('Helvetica', 16), command=self.solve_puzzle)
        self.clear_button = tk.CTkButton(self.btnframe, text="Clear All", font=('Helvetica', 16), command=lambda: self.reset_puzzle(1,0))
        self.mainframe.pack(side = "left",pady=10,padx=(10,5))
        self.board_frame.pack(padx=10, pady=10)
        self.btnframe.pack(fill="x")
        self.time_label.pack(pady=10)
        self.solve_button.pack(padx=(5, 10), side="left", fill="x", expand=True)
        self.clear_button.pack(padx=(0,5),pady=5,side="right", fill="x", expand=True)

        #board
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
                entry.bind('<Button-1>', self.select_cell)
                self.board[i][j] = entry

        #sub frame
        self.subframe = tk.CTkFrame(self.master)
        self.labelframe = tk.CTkFrame(self.subframe)
        self.history_button_frame = tk.CTkScrollableFrame(self.subframe)
        save_button = tk.CTkButton(self.labelframe ,text="💾", font=('Helvetica', 16), command=lambda:self.save_history,width=8)
        self.historylabel = tk.CTkLabel(self.labelframe,text="History",font=('Helvetica', 20))
        self.subframe.pack(padx=(5,10),pady=10, side="right",fill="both")
        self.labelframe.pack(padx = 5, fill="both")
        self.history_button_frame.pack(padx=(5,10),pady=10, side="right",fill="both")
        save_button.pack(side="left", padx=(5, 10))
        self.historylabel.pack()

        #menu
        self.menu = Menu(self.master)
        self.master.configure(menu=self.menu)
        
        filemenu= Menu(self.menu,tearoff=0)
        self.menu.add_cascade(label="file",menu=filemenu)
        filemenu.add_command(label="Open",command=self.open_puzzle)
        filemenu.add_command(label="Save",command=self.save_result)
        filemenu.add_separator()
        filemenu.add_command(label="Exit",foreground="red",command=self.exitQuestion)

        helpmenu= Menu(self.menu,tearoff=0)
        self.menu.add_cascade(label="help",menu=helpmenu)
        helpmenu.add_command(label="Version",command=self.version)

        self.load_history_from_file() 
        thread1 = threading.Thread(target=self.create_history_button)
        thread1.start()
        
        self.master.deiconify()


    def limit_input_length(self, event):
        entry = event.widget
        char = event.char

        if char == '\x08':
            event.widget.delete(0, tk.END)
        elif not char.isdigit() or len(entry.get()) >= 1 or char == "0":
            return "break"
    def create_history_button(self):
        # Start a new thread to create history buttons
        threading.Thread(target=self.create_history_buttons_thread).start()

    def create_history_buttons_thread(self):
        for idx, history_entry in enumerate(self.history_list):
            # Use after() to update the GUI on the main thread
            self.history_button_frame.after(0, self.create_history_button_gui, idx, history_entry)

    def create_history_button_gui(self, idx, history_entry):
        button_frame = tk.CTkFrame(self.history_button_frame)
        button_frame.pack(pady=5)
        after_button = tk.CTkButton(button_frame, text=f"History {idx + 1}", command=lambda idx=idx, entry=history_entry: self.show_solution(entry))
        CTkToolTip(after_button, message='\n'.join(['  '.join(map(str, row)) for row in history_entry]))
        after_button.pack(side="left", padx=(0, 2))

        remove_button = tk.CTkButton(button_frame, text=f"⛔", command=lambda idx=idx, entry=history_entry: self.remove_history(idx), width=8)
        remove_button.pack(side="right", padx=(0, 2))

    def load_history_from_file(self):
        if os.path.exists(self.history_file_path):
            with open(self.history_file_path, 'r') as file:
                lines = file.readlines()

            # Use eval to convert the string representation of a list to a list
            self.history_list = [eval(line.strip()) for line in lines]
    def save_history_to_file(self):
        # Keep a maximum of 100 histories
        if len(self.history_list) > 49:
            del self.history_list[0]

        with open(self.history_file_path, 'w') as file:
            for history_entry in self.history_list:
                # Save the list as a string representation
                file.write(str(history_entry) + '\n')
        return True
    def remove_history(self, idx):
        self.delete_history(idx)
        del self.history_list[idx]
        self.save_history_to_file()  # Save history after removing an entry
        self.update_history_buttons()
    def update_history_buttons(self):
        for widget in self.history_button_frame.winfo_children():
            widget.destroy()
        self.create_history_button()
    def save_history(self, puzzle):
        self.history_list.append([row[:] for row in puzzle])
        self.save_history_to_file()  # Save history after adding an entry
        self.update_history_buttons()
    def update_history_buttons(self):
        for widget in self.history_button_frame.winfo_children():
            widget.destroy()
        self.create_history_button()   
    def show_unsolvable_message(self):
        CTkMessagebox(title="Warning", message="Unsolvable puzzle",icon="warning", option_1="OK")
        self.reset_button.configure(state=tk.NORMAL)

        for i in range(9):
            for j in range(9):
                self.board[i][j].configure(state='normal')
    def reset_puzzle(self,mod,re):
        self.start_time = None
        self.elapsed_time = 0
        self.solved = 0
        self.time_label.configure(text="Elapse: 0s")
        self.solve_button.configure(text="Solve", command=self.solve_puzzle)
        if re == 1:
            self.reset_button.destroy()
            self.clear_button = tk.CTkButton(self.btnframe, text="Clear All", font=('Helvetica', 16), command=lambda: self.reset_puzzle(1,0))
            self.clear_button.pack(padx=(0,5),side="right", fill="x", expand=True)

        for i in range(9):
            for j in range(9):
                entry = self.board[i][j]
                if mod == 1:
                    entry.delete(0, tk.END)
                entry.configure(state='normal', font=('Helvetica', 20))
                if mod == 3:
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
            if self.is_solvable(puzzle):
                self.show_solution(puzzle)
                self.save_history(puzzle)
            else:
                self.show_unsolvable_message()
        else:
            self.show_unsolvable_message()
    def delete_history(self, idx):
        del self.history_list[idx]
        delete_message = CTkMessagebox(title="History Deleted", message="History entry deleted.", icon="info")
        self.save_history_to_file()
        self.update_history_buttons()

        # Show a message indicating that the history entry has been deleted


    def is_solvable(self, puzzle):
        # Create a copy of the puzzle
        puzzle_copy = [[puzzle[i][j] for j in range(9)] for i in range(9)]

        # Attempt to solve the puzzle again
        return self.solve_sudoku(puzzle_copy)
    def solve_sudoku(self, puzzle):
        empty_cell = next(((i, j) for i in range(9) for j in range(9) if puzzle[i][j] == 0), None)
        if not empty_cell:
            return True

        row, col = empty_cell
        for num in range(1, 10):
            start_row, start_col = 3 * (row // 3), 3 * (col // 3)
            if (
                num not in puzzle[row] and
                num not in [puzzle[i][col] for i in range(9)] and
                num not in [
                    puzzle[start_row + i][start_col + j]
                    for i in range(3)
                    for j in range(3)
                ]
            ):
                puzzle[row][col] = num

                if self.solve_sudoku(puzzle):
                    return True

                puzzle[row][col] = 0 

        return False
    def show_solution(self, puzzle):
        self.solved = 1
        self.highlight_3x3_area()

        for i, row_entries in enumerate(self.board):
            for j, entry in enumerate(row_entries):
                entry.delete(0, tk.END)
                entry.insert(0, str(puzzle[i][j]))
                entry.configure(font=('Helvetica', 20))

        if self.start_time is not None:  
            self.elapsed_time = round(time.time() - self.start_time, 2)
            self.time_label.configure(text=f"Elapse: {self.elapsed_time}s")
            self.start_time = None

        self.solve_button.configure(text="Save", command=self.save_result)
        self.clear_button.destroy()
        try:
            self.reset_button.destroy()
        except:
            pass
        self.reset_button = tk.CTkOptionMenu(self.btnframe, values=["Unlock", "Clear", "Reset"], command=self.resetMenu)
        self.reset_button.pack(padx=(0, 5), side="right", fill="x", expand=True)

    def select_cell(self, event):
        entry = event.widget
        for i, row_entries in enumerate(self.board):
            for j, board_entry in enumerate(row_entries):
                if board_entry == entry:
                    self.current_cell = (i, j)
                    row, col = self.current_cell
                    self.board[row][col].focus_set()
                    for i in range(9):
                        for j in range(9):
                            if i == row and j == col:
                                self.board[i][j].configure(font=('Helvetica', 20, 'bold'))
                            else:
                                self.board[i][j].configure(font=('Helvetica', 20))
                    self.highlight_3x3_area()

    def resetMenu(self,values):
        if values == "Unlock":
            self.reset_puzzle(2,1)
        elif values == "Clear":
            self.reset_puzzle(1,1)
        elif values == "Reset":
            self.reset_puzzle(3,1)
         
    def highlight_3x3_area(self):
        for i in range(9):
            for j in range(9):
                self.board[i][j].configure(bg='#FFFFFF')
        row, col = self.current_cell

        for i in range(9):
            for j in range(9):
                if i // 3 == row // 3 and j // 3 == col // 3 or i // 1 == row // 1 or j // 1 == col // 1:
                    if self.solved == 0:
                        self.board[i][j].configure(bg='#F5F6CE')

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

    def version(self):
        GUItitle = "A∐Ͳʘ SUDOKU SOLVER Version"
        name = "A∐Ͳʘ\nSUDOKU SOLVER"
        info = "Versio : 1.1.2 - Beta\n\nReleaseDate : December 01, 23\n\nDeveloper : wnsdn517"

        SudokuVer = tk.CTk()
        SudokuVer.resizable(0, 0)
        all_stuffs.hide(SudokuVer)
        SudokuVer.title(GUItitle)

        # Load the image using the Image class
        photo = PhotoImage("SUDOKU.png")

        logo_frame = tk.CTkFrame(SudokuVer)
        logo_frame.pack(pady=(5, 0), padx=2)

        logo_label = tk.CTkLabel(logo_frame, text="image")
        logo_label.pack(side="left", padx=5, pady=5)

        logo_text = tk.CTkLabel(logo_frame, text=name, font=("CookieRun.otf", 20, "bold"), text_color="#3AA3DB")
        logo_text.pack(padx=(15, 5), pady=5, side="right")

        moreinfo = tk.CTkFrame(SudokuVer)
        moreinfo.pack(pady=5, padx=2, fill="both")

        moretext = tk.CTkLabel(moreinfo, text=info, font=("CookieRun.otf", 15), justify="left")
        moretext.pack(padx=2, pady=2)

        exitbtn = tk.CTkButton(SudokuVer, text="Exit", fg_color="red", command=SudokuVer.destroy)
        exitbtn.pack(padx=(120, 0))

        SudokuVer.mainloop()

    def open_puzzle(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("text file", "*.txt")], title="Open File")
        if file_path:
            with open(file_path, 'r') as file:
                lines = file.readlines()

            if len(lines) != 9 or any(
                len(line.strip().split()) != 9 or any(not value.isdigit() and value != ' ' for value in line.strip().split())
                for line in lines
            ):
                CTkMessagebox(title="Error", message="Invalid file format.", icon="error", option_1="OK")
                return

            for i, line in enumerate(lines):
                values = line.strip().split()
                for j, value in enumerate(values):
                    if value.isdigit():
                        self.board[i][j].delete(0, tk.END)
                        self.board[i][j].insert(0, value)
    def save_result(self):
        if not self.solved:
            result = CTkMessagebox(title="Save Confirmation", message="The puzzle is not solved yet. Do you still want to save?",icon="question", option_1="Save", option_2="Cancel")
            if result.get() == 'Cancel':
                return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("text file", "*.txt")], title="Save As..")
        if file_path:
            with open(file_path, 'w') as file:
                for row_entries in self.board:
                    values = [entry.get() if entry.get() else ' ' for entry in row_entries]
                    file.write(' '.join(map(str, values)) + '\n')
            re = CTkMessagebox(title="Information", message="Sudoku puzzle saved successfully.", option_1="OK",option_2="Open")
            if re.get() == "Open":
                os.system(f"start notepad.exe \"{file_path}\"")

    def exitQuestion(self):
        result = CTkMessagebox(title="Exit?", message="Would you like to close the window?", icon="warning", option_1="Exit", option_2="Cancel")
        if result.get() == "Exit":
            save = tk.CTk()
            title_bar.hide(save)
            savelabel = tk.CTkLabel(save, text="Please wait.\nPreparing to close the Sudoku program.")
            savelabel.pack()
            self.save_history_to_file()
            save.after(300, exit)
            save.mainloop()

root = tk.CTk()
game = Sudoku(root)
root.mainloop()