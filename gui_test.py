import tkinter as tk
import tkinter.ttk as ttk

root = tk.Tk()
root.geometry("400x300")

outline = ttk.Frame(master=root)
outline.pack(fill="both", expand=True, padx=5, pady=5)
header = ttk.Frame(master=outline)
footer = ttk.Frame(master=outline)
container1 = ttk.Frame(master=outline)

header.pack(side="top", fill="both", expand=False)
footer.pack(side="bottom", fill="both", expand=False, padx=10, pady=5)
container1.pack(side="left", fill="both", expand=True)

next_button = ttk.Button(
    master=footer,
    text="次へ",
)
next_button.pack(side="right", ipady=3)
back_button = ttk.Button(
    master=footer,
    text="最初に戻る",
)
back_button.pack(side="left", ipady=3)

root.mainloop()
