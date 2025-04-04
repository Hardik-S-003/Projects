# viz.py

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import pandas as pd
import logging

def create_nutrition_chart(master, nutrition_df):
    """
    Creates and embeds a Matplotlib bar chart for nutritional data into a Tkinter frame.

    Args:
        master (tk.Frame): The Tkinter frame to embed the chart into.
        nutrition_df (pd.DataFrame): DataFrame containing nutritional information.

    Returns:
        FigureCanvasTkAgg: The Matplotlib canvas containing the chart.
    """
    try:
        # Create a new frame specifically for the chart
        chart_frame = tk.Frame(master)
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create figure and canvas
        nutrition_figure, nutrition_ax = plt.subplots(figsize=(6, 5), facecolor="#f0f0f0")
        nutrition_canvas = FigureCanvasTkAgg(nutrition_figure, master=chart_frame)
        nutrition_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        if nutrition_df is not None and not nutrition_df.empty:
            _plot_nutrition_data(nutrition_ax, nutrition_df)
        else:
            nutrition_ax.clear()
            nutrition_ax.text(0.5, 0.5, "Nutritional data not available", ha='center', va='center', fontsize=12, color="#777777")
        
        # This is critical - need to draw the canvas to make it appear
        nutrition_canvas.draw()
        
        logging.info("Nutrition chart created successfully")
        return nutrition_canvas
    
    except Exception as e:
        logging.error(f"Error creating nutrition chart: {e}")
        # Create a simple error message if chart creation fails
        error_frame = tk.Frame(master)
        error_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        error_label = tk.Label(error_frame, text="Error creating nutrition chart", fg="red")
        error_label.pack(pady=20)
        return None


def _plot_nutrition_data(ax, nutrition_df):
    """
    Plots the nutritional data on the provided Matplotlib axes.

    Args:
        ax (matplotlib.axes._subplots.AxesSubplot): The Matplotlib axes to plot on.
        nutrition_df (pd.DataFrame): DataFrame containing nutritional information.
    """
    try:
        ax.clear()
        
        # Filter for common important nutrients and ensure we have amount and unit columns
        if 'amount' not in nutrition_df.columns or nutrition_df.empty:
            ax.text(0.5, 0.5, "Invalid nutrition data format", ha='center', va='center', fontsize=12, color="red")
            return
            
        # Get the top nutrients by amount
        # Select only nutrients with meaningful amounts (> 0)
        valid_df = nutrition_df[nutrition_df['amount'] > 0]
        
        # If we have units, combine with amount for display
        if 'unit' in nutrition_df.columns:
            valid_df['display_value'] = valid_df['amount'].round(1).astype(str) + ' ' + valid_df['unit']
        else:
            valid_df['display_value'] = valid_df['amount'].round(1).astype(str)
            
        # Select top nutrients for plotting
        top_nutrients = valid_df.nlargest(8, 'amount')
        
        if len(top_nutrients) > 0:
            nutrients = top_nutrients['name']
            amounts = top_nutrients['amount']
            
            # Create horizontal bar chart for better readability
            bars = ax.barh(nutrients, amounts, color="#2ecc71")
            
            # Add value labels to the end of each bar
            for i, bar in enumerate(bars):
                value = top_nutrients['display_value'].iloc[i]
                ax.text(bar.get_width() + (max(amounts) * 0.02), 
                        bar.get_y() + bar.get_height()/2, 
                        value, 
                        va='center',
                        fontsize=9)
                
            ax.set_title("Key Nutrients", fontsize=14, fontweight='bold', color="#333333")
            ax.set_xlabel("Amount", fontsize=10, color="#555555")
            ax.set_ylabel("Nutrients", fontsize=10, color="#555555")
            ax.tick_params(axis='y', labelsize=9)
            ax.tick_params(axis='x', labelsize=9)
            ax.grid(axis='x', linestyle='--', alpha=0.7)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        else:
            ax.text(0.5, 0.5, "No significant nutrient data available", 
                    ha='center', va='center', fontsize=12, color="#777777")
    
    except Exception as e:
        logging.error(f"Error plotting nutrition data: {e}")
        ax.clear()
        ax.text(0.5, 0.5, f"Error plotting data", ha='center', va='center', fontsize=12, color="red")