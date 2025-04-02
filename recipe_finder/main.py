import tkinter as tk
import gui 

def main():
    root = tk.Tk()
    app = gui.RecipeApp(root) 
    root.mainloop()  
    
if __name__ == '__main__':
    main()