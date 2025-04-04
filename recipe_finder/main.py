#   main.py

import tkinter as tk
import threading
import core
import gui
import viz
from tkinter import messagebox
import logging

#   Configure logging
logging.basicConfig(level=logging.INFO, filename="logs/app.log",
                    format="%(asctime)s - %(levelname)s - %(message)s")


class RecipeApp:

    def __init__(self, root):
        self.root = root
        self.recipe_gui = gui.RecipeGUI(master=self.root)
        self.recipe_gui.search_button.config(command=self.search_recipes)
        self.recipe_gui.results_listbox.bind("<<ListboxSelect>>", self.show_recipe_details)
        self.nutrition_canvas = None  # Placeholder for the chart

    def search_recipes(self):
        ingredients = self.recipe_gui.ingredients_entry.get()
        cuisine = self.recipe_gui.cuisine_var.get()
        diet = self.recipe_gui.diet_var.get()

        if not ingredients:
            messagebox.showwarning("Input Required",
                                    "Please enter ingredients to search for.")
            return

        self.recipe_gui.status_label.config(text="Searching...")
        self.root.update_idletasks()
        threading.Thread(target=self._perform_search,
                        args=(ingredients, cuisine, diet)).start()

    def _perform_search(self, ingredients, cuisine, diet):
        try:
            recipes = core.search_recipes(ingredients=ingredients,
                                        cuisine=cuisine,
                                        diet=diet)
            self.root.after(0, self._update_results_callback, recipes)
        except Exception as e:
            logging.error(f"Error during recipe search: {e}")
            self.root.after(0, self._show_error,
                            "Error searching recipes. Please check logs.")

    def _update_results_callback(self, recipes):
        try:
            self.recipe_gui.update_results(recipes)
            self.recipe_gui.status_label.config(text="Search complete.")
        except Exception as e:
            logging.error(f"Error updating results: {e}")
            self.root.after(0, self._show_error,
                            "Error displaying search results. Please check logs.")

    def show_recipe_details(self, event):
        selected_recipe_index = self.recipe_gui.results_listbox.curselection()
        if selected_recipe_index:
            try:
                recipe_title_with_id = self.recipe_gui.results_listbox.get(
                    selected_recipe_index)
                recipe_id = int(recipe_title_with_id.split("(")[-1][:-1])
                self.recipe_gui.status_label.config(
                    text="Loading recipe details...")
                self.root.update_idletasks()
                threading.Thread(target=self._perform_show_details,
                                args=(recipe_id,)).start()
            except ValueError as ve:
                logging.error(f"Value error processing recipe ID: {ve}")
                self.root.after(
                    0, self._show_error,
                    "Error processing recipe selection. Please check logs.")
            except Exception as e:
                logging.error(f"Unexpected error in show_recipe_details: {e}")
                self.root.after(
                    0, self._show_error,
                    "Unexpected error. Please check logs.")

    def _perform_show_details(self, recipe_id):
        try:
            recipe_details = core.get_recipe_details_with_nutrition(
                recipe_id)  # Fetch with nutrition
            self.root.after(0, self._update_details_callback,
                            recipe_details)
        except Exception as e:
            logging.error(f"Error fetching recipe details: {e}")
            self.root.after(0, self._show_error,
                            "Error fetching details. Please check logs.")

    def _update_details_callback(self, recipe_details):
        try:
            self._update_details(recipe_details)
        except Exception as e:
            logging.error(f"Error in _update_details_callback: {e}")
            self.root.after(
                0, self._show_error,
                "Error displaying details or chart. Please check logs.")

    def _update_details(self, recipe_details):
        try:
            # Update recipe text details
            self.recipe_gui.update_details(recipe_details)
            
            # Process nutrition data
            nutrition_df = core.analyze_nutrition(recipe_details)
            
            logging.info(f"Nutrition data shape: {nutrition_df.shape if nutrition_df is not None else 'None'}")
            
            # Clear previous chart if it exists
            if self.nutrition_canvas:
                try:
                    self.nutrition_canvas.get_tk_widget().destroy()
                except Exception as e:
                    logging.error(f"Error destroying previous chart: {e}")
            
            # Create and embed nutrition chart
            self.nutrition_canvas = viz.create_nutrition_chart(
                self.recipe_gui.details_frame, nutrition_df)
            
            self.recipe_gui.status_label.config(text="Ready")
            
        except Exception as e:
            logging.error(f"Error updating details or creating chart: {e}")
            self.root.after(
                0, self._show_error,
                "Error displaying details or chart. Please check logs.")

    def _show_error(self, message):
        messagebox.showerror("Error", message)
        self.recipe_gui.status_label.config(text="Error")

def main():
    root = tk.Tk()
    root.title("Recipe Finder with Nutrition Analysis")
    root.geometry("1200x800")  # Increased width for better chart display
    app = RecipeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()