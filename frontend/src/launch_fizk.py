import tkinter as tk
from utils.fizk_seed_generator import FizkSeedGenerator

if __name__ == "__main__":    
  root = tk.Tk()    
  app = FizkSeedGenerator(root)    
  root.mainloop()