from MenuUi import MenuTerminal, MenuGui
import tkinter as tk

if __name__ == "__main__":

    choice = input(f"""
Usage: [g | t]
g : use GUI
t : use Terminal
""")
    
    if choice == "g":
        master = tk.Tk()
        guiTerminal = MenuGui(master)
        master.mainloop()
    elif choice == "t":
        menuTerminal = MenuTerminal()
        menuTerminal.run()
    else:
        print("Invalid choice")