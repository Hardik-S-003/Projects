import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter import PhotoImage  
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import core  
import threading 

class RecipeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recipe Finder with Nutrition Analysis")
        self.root.geometry("800x600") 

        # --- Styling ---
        self.style = ttk.Style()
        self.style.configure("TButton", padding=5, font=('Helvetica', 10))
        self.style.configure("TLabel", font=('Helvetica', 12))
        self.style.configure("TEntry", font=('Helvetica', 12))
        self.style.configure("TText", font=('Helvetica', 10))

        # --- Frames ---
        self.input_frame = ttk.Frame(self.root, padding=10)
        self.input_frame.pack(fill=tk.X)

        self.results_frame = ttk.Frame(self.root, padding=10)
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        self.details_frame = ttk.Frame(self.root, padding=10)
        self.details_frame.pack(fill=tk.BOTH, expand=True)

        # --- Input Elements ---
        ttk.Label(self.input_frame, text="Ingredients:").grid(row=0, column=0, padx=5, pady=5)
        self.ingredients_entry = ttk.Entry(self.input_frame, width=30)
        self.ingredients_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.input_frame, text="Cuisine:").grid(row=0, column=2, padx=5, pady=5)
        self.cuisine_entry = ttk.Entry(self.input_frame, width=20)
        self.cuisine_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(self.input_frame, text="Diet:").grid(row=0, column=4, padx=5, pady=5)
        self.diet_var = tk.StringVar()
        self.diet_combobox = ttk.Combobox(self.input_frame, textvariable=self.diet_var,
                                        values=["", "Vegetarian", "Vegan", "Gluten Free"]) 
        self.diet_combobox.grid(row=0, column=5, padx=5, pady=5)

        self.search_button = ttk.Button(self.input_frame, text="Search Recipes", command=self.search_recipes)
        self.search_button.grid(row=0, column=6, padx=5, pady=5)

        # --- Results Listbox ---
        self.results_listbox = tk.Listbox(self.results_frame, height=15, selectbackground="lightblue")
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_listbox.bind('<<ListboxSelect>>', self.show_recipe_details)

        self.results_scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.results_listbox.yview)
        self.results_listbox['yscrollcommand'] = self.results_scrollbar.set
        self.results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Details Display ---
        self.details_text = scrolledtext.ScrolledText(self.details_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.details_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.image_label = ttk.Label(self.details_frame)
        self.image_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.nutrition_figure, self.nutrition_ax = plt.subplots(figsize=(4, 3))
        self.nutrition_canvas = FigureCanvasTkAgg(self.nutrition_figure, master=self.details_frame)
        self.nutrition_canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # --- Status Bar ---
        self.status_label = ttk.Label(self.root, text="Ready", anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def search_recipes(self):
        ingredients = self.ingredients_entry.get()
        cuisine = self.cuisine_entry.get()
        diet = self.diet_var.get()

        if not ingredients:
            messagebox.showwarning("Input Required", "Please enter ingredients to search for.")
            return

        self.status_label.config(text="Searching...")
        self.root.update_idletasks()  

        threading.Thread(target=self._perform_search, args=(ingredients, cuisine, diet)).start()

    def _perform_search(self, ingredients, cuisine, diet):
        """
        Performs the actual API search and updates the GUI.  This runs in a separate thread.
        """

        recipes = core.search_recipes(ingredients=ingredients, cuisine=cuisine, diet=diet)

        self.root.after(0, self._update_results_listbox, recipes) 

    def _update_results_listbox(self, recipes):
        """
        Updates the results listbox with the search results.  This runs on the main thread.
        """
        self.results_listbox.delete(0, tk.END)  
        if recipes and recipes.get('results'):
            for recipe in recipes['results']:
                self.results_listbox.insert(tk.END, f"{recipe['title']} ({recipe['id']})")
        else:
            self.results_listbox.insert(tk.END, "No recipes found.")
        self.status_label.config(text="Search complete.")

    def show_recipe_details(self, event):
        selected_recipe_index = self.results_listbox.curselection()
        if selected_recipe_index:
            recipe_title_with_id = self.results_listbox.get(selected_recipe_index)
            recipe_id = int(recipe_title_with_id.split('(')[-1][:-1]) 
            self.status_label.config(text="Loading recipe details...")
            self.root.update_idletasks()

            threading.Thread(target=self._fetch_and_display_details, args=(recipe_id,)).start()

    def _fetch_and_display_details(self, recipe_id):
        """
        Fetches recipe details from the API and displays them.  Runs in a separate thread.
        """
        recipe_details = core.get_recipe_details(recipe_id)
        self.root.after(0, self._update_details_display, recipe_details)

    def _update_details_display(self, recipe_details):
        """
        Updates the GUI with the recipe details.  Runs on the main thread.
        """
        self.details_text.config(state=tk.NORMAL)  
        self.details_text.delete("1.0", tk.END)

        if recipe_details:
            title = recipe_details.get('title', 'No Title')
            ingredients = "\n".join(
                [f"- {ing['original']}" for ing in recipe_details.get('extendedIngredients', [])])
            instructions = recipe_details.get('instructions', 'No Instructions')

            details_string = f"Title: {title}\n\nIngredients:\n{ingredients}\n\nInstructions:\n{instructions}"
            self.details_text.insert(tk.END, details_string)

            # --- Display Image ---
            image_url = recipe_details.get('image')
            if image_url:
                try:
                    import urllib.request
                    import io
                    image_data = urllib.request.urlopen(image_url).read()
                    pil_image = Image.open(io.BytesIO(image_data))
                    tk_image = ImageTk.PhotoImage(pil_image)
                    self.image_label.config(image=tk_image)
                    self.image_label.image = tk_image  
                except Exception as e:
                    print(f"Error loading image: {e}")
                    self.image_label.config(image=None)
                    self.image_label.config(text="Image not available")
            else:
                self.image_label.config(image=None)
                self.image_label.config(text="Image not available")

            # --- Nutrition Analysis and Plotting ---
            nutrition_df = core.analyze_nutrition(recipe_details)
            if nutrition_df is not None:
                self._plot_nutrition_data(nutrition_df)
            else:
                self.nutrition_ax.clear()
                self.nutrition_ax.text(0.5, 0.5, "Nutritional data not available", ha='center', va='center')
                self.nutrition_canvas.draw()

        else:
            self.details_text.insert(tk.END, "Failed to fetch recipe details.")
            self.image_label.config(image=None)
            self.image_label.config(text="Details not available")
            self.nutrition_ax.clear()
            self.nutrition_ax.text(0.5, 0.5, "Details not available", ha='center', va='center')
            self.nutrition_canvas.draw()

        self.details_text.config(state=tk.DISABLED)  
        self.status_label.config(text="Ready")

    def _plot_nutrition_data(self, nutrition_df):
        """
        Plots the nutritional data using Matplotlib.
        """
        self.nutrition_ax.clear() 

        # Select top nutrients for plotting 
        top_nutrients = nutrition_df.nlargest(10, 'amount')
        nutrients = top_nutrients['name']
        amounts = top_nutrients['amount']

        self.nutrition_ax.bar(nutrients, amounts)
        self.nutrition_ax.set_title("Top Nutrients")
        self.nutrition_ax.set_ylabel("Amount")
        self.nutrition_ax.tick_params(axis='x', rotation=45)  

        self.nutrition_canvas.draw()  

def main():
    root = tk.Tk()
    app = RecipeApp(root)
    root.mainloop()

if __name__ == '__main__':
    from PIL import Image, ImageTk 
    main()
