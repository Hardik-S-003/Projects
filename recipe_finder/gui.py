# gui.py

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class RecipeGUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        # --- Styling ---
        self.style = ttk.Style()
        self.style.configure("TButton", padding=5, font=('Ubuntu', 12))
        self.style.configure("TLabel", font=('Ubuntu', 14))
        self.style.configure("TEntry", font=('Ubuntu', 14))
        self.style.configure("TText", font=('Ubuntu Mono', 10))

        # --- Input Frame ---
        self.input_frame = ttk.Frame(self, padding=15)
        self.input_frame.pack(fill=tk.X)

        ttk.Label(self.input_frame, text="Ingredients:", foreground="#3498db").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ingredients_entry = ttk.Entry(self.input_frame, width=40)
        self.ingredients_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.input_frame, text="Cuisine:", foreground="#3498db").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.cuisine_var = tk.StringVar()
        self.cuisine_combobox = ttk.Combobox(self.input_frame, textvariable=self.cuisine_var,
                                            values=["", "African", "Asian", "American", "British", "Cajun", "Caribbean",
                                                    "Chinese", "Eastern European", "European", "French", "German", "Greek",
                                                    "Indian", "Irish", "Italian", "Japanese", "Jewish", "Korean", "Latin American",
                                                    "Mediterranean", "Mexican", "Middle Eastern", "Nordic", "Southern", "Spanish",
                                                    "Thai", "Vietnamese"])
        self.cuisine_combobox.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(self.input_frame, text="Diet:", foreground="#3498db").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.diet_var = tk.StringVar()
        self.diet_combobox = ttk.Combobox(self.input_frame, textvariable=self.diet_var,
                                        values=["", "Vegetarian", "Vegan", "Gluten Free", "Non-Veg"])
        self.diet_combobox.grid(row=0, column=5, padx=5, pady=5)

        self.search_button = ttk.Button(self.input_frame, text="Find Recipes", command=self.search_recipes, style="Accent.TButton")
        self.search_button.grid(row=0, column=6, padx=10, pady=5)

        # --- Results Frame ---
        self.results_frame = ttk.Frame(self, padding=15)
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        self.results_listbox = tk.Listbox(self.results_frame, height=15, selectbackground="#a8d5ff", selectforeground="black")
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_listbox.bind('<<ListboxSelect>>', self.show_recipe_details)

        self.results_scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.results_listbox.yview)
        self.results_listbox['yscrollcommand'] = self.results_scrollbar.set
        self.results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Details Frame - Modified to have two sections side by side ---
        self.details_frame = ttk.Frame(self, padding=15)
        self.details_frame.pack(fill=tk.BOTH, expand=True)

        # Left side for text details
        self.details_left_frame = ttk.Frame(self.details_frame)
        self.details_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.details_text = scrolledtext.ScrolledText(self.details_left_frame, wrap=tk.WORD, 
                                                      state=tk.DISABLED, background="#f0f0f0", 
                                                      foreground="#333333", height=10)
        self.details_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.image_label = ttk.Label(self.details_left_frame, background="#ffffff")
        self.image_label.pack(side=tk.TOP, padx=10, pady=10)

        # Right side will be used for the nutrition chart in viz.py

        # --- Status Bar ---
        self.status_label = ttk.Label(self, text="Ready", anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Accent Button Style ---
        self.style.configure("Accent.TButton",
                             background="#4CAF50",
                             foreground="white",
                             font=('Ubuntu', 12, 'bold'))
        self.style.map("Accent.TButton",
                       background=[("active", "#45a049"),
                                   ("pressed", "#3d8e40")])

    def search_recipes(self):
        pass  # To be implemented in main.py

    def show_recipe_details(self, event):
        pass  # To be implemented in main.py

    def update_results(self, recipes):
        self.results_listbox.delete(0, tk.END)
        if recipes and recipes.get('results'):
            for recipe in recipes['results']:
                self.results_listbox.insert(tk.END, f"{recipe['title']} ({recipe['id']})")
        else:
            self.results_listbox.insert(tk.END, "No recipes found.")

    def update_details(self, details):
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)

        if details:
            title = details.get('title', 'No Title')
            ingredients = "\n".join([f"- {ing['original']}" for ing in details.get('extendedIngredients', [])])
            instructions = details.get('instructions', 'No Instructions')

            details_string = f"Title: {title}\n\nIngredients:\n{ingredients}\n\nInstructions:\n{instructions}"
            self.details_text.insert(tk.END, details_string)

            # --- Display Image ---
            image_url = details.get('image')
            if image_url:
                try:
                    import urllib.request
                    import io
                    from PIL import Image, ImageTk  # Import here to avoid errors if not running GUI
                    image_data = urllib.request.urlopen(image_url).read()
                    pil_image = Image.open(io.BytesIO(image_data))
                    
                    # Resize image to fit better in the UI
                    pil_image = pil_image.resize((300, 200), Image.LANCZOS)
                    
                    tk_image = ImageTk.PhotoImage(pil_image)
                    self.image_label.config(image=tk_image)
                    self.image_label.image = tk_image  # Keep a reference
                except Exception as e:
                    print(f"Error loading image: {e}")
                    self.image_label.config(image=None)
                    self.image_label.config(text="Image not available")
            else:
                self.image_label.config(image=None)
                self.image_label.config(text="Image not available")
        else:
            self.details_text.insert(tk.END, "Failed to fetch recipe details.")
            self.image_label.config(image=None)
            self.image_label.config(text="Details not available")

        self.details_text.config(state=tk.DISABLED)