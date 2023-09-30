import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import os
from sklearn.linear_model import LinearRegression

# Define residuals as a global variable
residuals = None
predictions = None  # Initialize predictions variable

def find_all_peaks(y_axis):
    return find_peaks(y_axis, height=y_axis, distance=1000)

def remove_noisy_peaks(pulses, found_peaks):
    peak_heights = found_peaks[1]['peak_heights']
    peak_positions = pulses[found_peaks[0]]

    new_positions = []
    new_heights = []

    peak_mean = np.average(peak_heights)

    for i in range(0, len(peak_heights) - 1):
        if peak_heights[i] > peak_mean:
            new_heights.append(peak_heights[i])
            new_positions.append(peak_positions[i])

    return new_positions, new_heights

def draw_peaks(pulses, y_axis, peak_pos, peak_h):
    global predictions, residuals  # Access global predictions and residuals variables
    print(f"First peak position: {peak_pos[0]}, height: {peak_h[0]}")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.plot(pulses, y_axis)
    ax1.set_title("Original Data")
    ax1.set_xlabel("X-axis")
    ax1.set_ylabel("Y-axis")

    ax2.plot(pulses, y_axis, label='Original Data')
    ax2.scatter(peak_pos[0], peak_h[0], color='r', s=15, marker='D', label='Maxima')
    
    if predictions is not None:
        ax2.plot(pulses, predictions, label='Predicted Data', linestyle='--')
        
        # Calculate residuals (difference between original and predicted data)
        residuals = y_axis - predictions
        ax2.plot(pulses, residuals, label='Residuals', linestyle='-.')  # Plot residuals
    
    ax2.set_title("Original vs. Predicted Data")
    ax2.set_xlabel("X-axis")
    ax2.set_ylabel("Y-axis")
    ax2.legend()
    
    plt.show()

def read_xlsx_file(path, starting_column, row_number):
    df = pd.read_excel(path)
    selected_row = df.iloc[row_number - 1, starting_column:].values
    return selected_row.astype(float)

def get_pulse_data():
    file_path = filedialog.askopenfilename(title="Select an Excel file")  # Use a file dialog to select a file

    if not file_path:
        return

    # Display only the filename
    selected_filename_label.config(text=os.path.basename(file_path))

    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, file_path)

def process_and_plot():
    global predictions  # Access the global predictions variable
    file_path = file_path_entry.get()
    starting_col = starting_column_entry.get()
    row_number = row_number_entry.get()

    if not starting_col or not row_number:
        messagebox.showerror("Error", "Please enter both starting column and row number.")
        return

    try:
        starting_col = int(starting_col)
        row_number = int(row_number)
    except ValueError:
        messagebox.showerror("Error", "Starting column and row number must be integers.")
        return

    yaxis = np.array(read_xlsx_file(file_path, starting_col, row_number))
    pulses = np.array(list(range(0, len(yaxis))))

    if len(yaxis) == 0:
        messagebox.showerror("Error", "No data found in the selected row.")
        return

    peaks = find_all_peaks(yaxis)
    peak_positions, peak_heights = remove_noisy_peaks(pulses, peaks)
    
    # Initialize predictions here
    predictions = np.zeros(len(yaxis))  # Initialize as zeros or with appropriate values

    # Create a progress bar
    progress_bar = ttk.Progressbar(root, mode='indeterminate')
    progress_bar.pack(pady=10)
    progress_bar.start()

    # Update the GUI
    root.update_idletasks()

    # Perform time-consuming processing (plotting)
    draw_peaks(pulses, yaxis, peak_positions, peak_heights)

    # Stop the progress bar
    progress_bar.stop()
    progress_bar.destroy()

    # Simple Machine Learning Approach
    feature = yaxis  # You can change this feature to any other column in the Excel file
    target = np.random.rand(len(yaxis))  # Placeholder for target values (replace with actual target values)

    # Create a linear regression model
    model = LinearRegression()
    model.fit(feature.reshape(-1, 1), target)

    # Predict target values
    predictions = model.predict(feature.reshape(-1, 1))

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Peak Finder")

    file_path_label = tk.Label(root, text="Select an Excel file:")
    file_path_label.pack(pady=5)

    browse_button = tk.Button(root, text="Browse", command=get_pulse_data)
    browse_button.pack(pady=5)

    input_frame = tk.Frame(root)
    input_frame.pack(pady=10)

    file_path_entry = tk.Entry(input_frame)
    file_path_entry.grid(row=0, column=0, columnspan=2, padx=5)

    starting_column_label = tk.Label(input_frame, text="Starting Column:")
    starting_column_label.grid(row=1, column=0, padx=5)

    starting_column_entry = tk.Entry(input_frame)
    starting_column_entry.grid(row=1, column=1, padx=5)

    row_number_label = tk.Label(input_frame, text="Row Number:")
    row_number_label.grid(row=2, column=0, padx=5)

    row_number_entry = tk.Entry(input_frame)
    row_number_entry.grid(row=2, column=1, padx=5)

    submit_button = tk.Button(root, text="Submit", command=process_and_plot)
    submit_button.pack(pady=10)

    # Add a label to display the selected filename
    selected_filename_label = tk.Label(root, text="", font=("Helvetica", 10))
    selected_filename_label.pack(pady=5)

    root.mainloop()
