import tkinter as tk

root = tk.Tk()
root.title("测试 Tkinter")
root.geometry("300x200")
tk.Label(root, text="Hello, tkinter!").pack()
root.mainloop()