# Save this code as todo_app_gui.py

import tkinter
import customtkinter as ctk
import json
import os
from datetime import datetime

# --- Constants ---
TASKS_FILE = "tasks_gui.json" # Will be created in the same directory as the script
APP_NAME = "My To-Do List"
WINDOW_WIDTH = 550
WINDOW_HEIGHT = 600

# --- Appearance Settings (Modify as desired) ---
# Modes: "System" (default), "Dark", "Light"
ctk.set_appearance_mode("System")
# Themes: "blue" (default), "green", "dark-blue"
ctk.set_default_color_theme("blue")

# --- Core Functions ---

def load_tasks(filename=TASKS_FILE):
    """Loads tasks from a JSON file."""
    if not os.path.exists(filename):
        return []
    # Check if file is empty
    if os.path.getsize(filename) == 0:
        print(f"Warning: '{filename}' is empty. Starting fresh.")
        return []
    try:
        with open(filename, 'r') as f:
            tasks = json.load(f)
            if not isinstance(tasks, list):
                print(f"Warning: '{filename}' format incorrect. Starting fresh.")
                return []
            # Ensure essential keys exist (add defaults if missing)
            for task in tasks:
                task.setdefault('description', 'No Description')
                task.setdefault('done', False)
                # Add timestamp if missing from older format, handle potential errors
                if 'timestamp' not in task:
                     # Provide a default past timestamp or handle as needed
                     task['timestamp'] = datetime(1970, 1, 1).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    # Basic validation/correction of timestamp format if needed (optional)
                    try:
                        datetime.strptime(task['timestamp'], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                         print(f"Warning: Correcting invalid timestamp format for task: {task.get('description')}")
                         task['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Or a default

            return tasks
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading tasks from '{filename}': {e}. Starting fresh.")
        return []
    except Exception as e: # Catch other potential errors during loading/processing
        print(f"An unexpected error occurred loading tasks: {e}. Starting fresh.")
        return []


def save_tasks(tasks, filename=TASKS_FILE):
    """Saves the current list of tasks to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(tasks, f, indent=4)
    except IOError as e:
        print(f"Error saving tasks to '{filename}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred saving tasks: {e}")


# --- Main Application Class ---

class TodoApp(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tasks = load_tasks()

        # --- Window Setup ---
        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100) # Allow some resizing

        # --- Configure Grid Layout ---
        self.grid_columnconfigure(0, weight=1) # Allow main frame to expand horizontally
        self.grid_rowconfigure(2, weight=1)    # Allow task list frame to expand vertically

        # --- Title Label ---
        self.title_label = ctk.CTkLabel(self, text=APP_NAME, font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # --- Input Frame ---
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent") # Use transparent to show window bg
        self.input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="new")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.task_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Enter new task...", width=350)
        self.task_entry.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        self.task_entry.bind("<Return>", self.add_task_event) # Bind Enter key

        self.add_button = ctk.CTkButton(self.input_frame, text="Add Task", command=self.add_task_event, width=100)
        # Example of gradient-like effect using different fg/hover colors
        self.add_button.configure(fg_color="#36719F", hover_color="#2A557F")
        self.add_button.grid(row=0, column=1, pady=10, sticky="e")

        # --- Task List Frame (Scrollable) ---
        self.task_list_frame = ctk.CTkScrollableFrame(self, label_text="Tasks")
        # Set background color for a layered/gradient *effect*
        self.task_list_frame.configure(fg_color=("#dbdbdb", "#2b2b2b")) # Light/Dark mode colors
        self.task_list_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.task_list_frame.grid_columnconfigure(0, weight=1) # Allow task content to expand

        # --- Initial Task Display ---
        self.refresh_task_list()

        # --- Save on Close ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_gradient_frame(self, parent):
        """ Creates a frame with a slightly different background for visual separation. """
        # You can customize colors here for a more pronounced 'gradient' layer
        # Getting the theme's default frame color dynamically
        frame_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        frame = ctk.CTkFrame(parent, fg_color=frame_color, corner_radius=5)
        frame.grid_columnconfigure(1, weight=1) # Allow label to expand
        return frame

    def refresh_task_list(self):
        """Clears and redraws the tasks in the scrollable frame."""
        # Clear existing task widgets
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()

        # Sort tasks: incomplete first, then by timestamp (newest first is tricky with strptime, let's do oldest first)
        try:
            sorted_tasks = sorted(
                self.tasks,
                key=lambda t: datetime.strptime(t.get('timestamp', '1970-01-01 00:00:00'), "%Y-%m-%d %H:%M:%S")
            )
            # Then sort by completion status (incomplete first)
            sorted_tasks = sorted(sorted_tasks, key=lambda t: t.get('done', False))
        except ValueError as e:
             print(f"Error sorting tasks by timestamp: {e}. Displaying unsorted.")
             # Fallback: Sort only by completion status if timestamps are bad
             sorted_tasks = sorted(self.tasks, key=lambda t: t.get('done', False))


        if not sorted_tasks:
             no_task_label = ctk.CTkLabel(self.task_list_frame, text="No tasks yet!", text_color="gray")
             no_task_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
             return

        # Add tasks to the frame
        for index, task in enumerate(sorted_tasks):
            task_frame = self.create_gradient_frame(self.task_list_frame)
            task_frame.grid(row=index, column=0, padx=5, pady=(5,0), sticky="ew")

            # Task Description Label
            task_text = task.get('description', 'N/A')
            is_done = task.get('done', False)
            text_color = "gray" if is_done else ctk.ThemeManager.theme["CTkLabel"]["text_color"]
            font_style = ctk.CTkFont(slant="italic" if is_done else "roman", overstrike=is_done)

            task_label = ctk.CTkLabel(
                task_frame,
                text=task_text,
                font=font_style,
                text_color=text_color,
                wraplength=300, # Wrap long text
                justify="left",
                anchor="w" # Align text to the west (left)
            )
            task_label.grid(row=0, column=1, padx=10, pady=(5, 0), sticky="ew") # Use ew sticky

            # Timestamp Label
            timestamp_str = task.get('timestamp', 'N/A')
            timestamp_label = ctk.CTkLabel(
                task_frame,
                text=f"Added: {timestamp_str}",
                font=ctk.CTkFont(size=9),
                text_color="gray",
                anchor="w" # Align text to the west (left)
            )
            timestamp_label.grid(row=1, column=1, padx=10, pady=(0, 5), sticky="ew") # Use ew sticky


            # Complete/Undo Button
            complete_text = "Undo" if is_done else "Complete"
            complete_fg_color = ("gray60", "gray30") if is_done else ctk.ThemeManager.theme["CTkButton"]["fg_color"]
            complete_hover_color = ("gray70", "gray40") if is_done else ctk.ThemeManager.theme["CTkButton"]["hover_color"]

            complete_button = ctk.CTkButton(
                task_frame,
                text=complete_text,
                width=70,
                fg_color=complete_fg_color,
                hover_color=complete_hover_color,
                command=lambda t=task: self.toggle_complete(t) # Pass the specific task dict
            )
            complete_button.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky="e")

            # Remove Button
            remove_button = ctk.CTkButton(
                task_frame,
                text="Remove",
                width=70,
                fg_color="#D32F2F", # Red color for delete
                hover_color="#B71C1C",
                command=lambda t=task: self.remove_task(t) # Pass the specific task dict
            )
            remove_button.grid(row=0, column=3, rowspan=2, padx=(0, 5), pady=5, sticky="e")

    def add_task_event(self, event=None): # event=None allows calling without keybind event
        """Adds a task from the entry field."""
        description = self.task_entry.get().strip()
        if description:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_task = {
                "description": description,
                "done": False,
                "timestamp": now
            }
            self.tasks.append(new_task)
            save_tasks(self.tasks) # Save immediately
            self.task_entry.delete(0, ctk.END) # Clear entry field
            self.refresh_task_list() # Update the display
        else:
            # Optionally show a small warning or do nothing
            print("Task description cannot be empty.")
            # You could use tkinter.messagebox here, but it looks dated with CTk
            # Consider a temporary label or disabling the add button briefly


    def toggle_complete(self, task_to_toggle):
        """Marks a task as done or not done."""
        found = False
        for i, task in enumerate(self.tasks):
             # Using index might be slightly more reliable if descriptions/timestamps could collide,
             # but matching dict content is generally fine if timestamps are unique enough.
             if task['timestamp'] == task_to_toggle['timestamp'] and task['description'] == task_to_toggle['description']:
                self.tasks[i]['done'] = not task.get('done', False)
                found = True
                break
        if found:
            save_tasks(self.tasks)
            self.refresh_task_list()
        else:
             print(f"Warning: Could not find task to toggle: {task_to_toggle.get('description')}")


    def remove_task(self, task_to_remove):
        """Removes a task from the list."""
        initial_len = len(self.tasks)
        # Create a new list excluding the task to remove
        # Matching both description and timestamp for better certainty
        self.tasks = [
            task for task in self.tasks
            if not (task.get('timestamp') == task_to_remove.get('timestamp') and
                    task.get('description') == task_to_remove.get('description'))
        ]

        if len(self.tasks) < initial_len: # Check if a task was actually removed
            save_tasks(self.tasks)
            self.refresh_task_list()
        else:
            print(f"Warning: Could not find task to remove: {task_to_remove.get('description')}")


    def on_closing(self):
        """Saves tasks when the window is closed."""
        print("Saving tasks before closing...")
        save_tasks(self.tasks) # Ensure tasks are saved
        self.destroy() # Close the window

# --- Run the Application ---
if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()