from tkinter import ttk  # Normal Tkinter.* widgets are not themed!
from ttkthemes import ThemedTk

# light themes
# window = ThemedTk(theme="arc")
# window = ThemedTk(theme="kroc")
# window = ThemedTk(theme="ubuntu")

# dark themes
window = ThemedTk(theme="black")
#window = ThemedTk(theme="equilux")

ttk.Button(window, text="Quit", command=window.destroy).pack()
window.mainloop()