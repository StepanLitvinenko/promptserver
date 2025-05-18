import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        # Source Code Files Section
        source_frame = tk.LabelFrame(self, text="Source Code Files (space or newline separated)")
        source_frame.pack(fill="x", padx=5, pady=5)

        self.source_text = tk.Text(source_frame, height=5)
        self.source_text.pack(fill="x", padx=5, pady=5)

        source_buttons = tk.Frame(source_frame)
        source_buttons.pack(fill="x", padx=5, pady=5)

        tk.Button(source_buttons, text="Select Files",
                  command=lambda: self.select_files(self.source_text)).pack(side="left")
        tk.Button(source_buttons, text="Select Directory",
                  command=lambda: self.select_directory(self.source_text)).pack(side="left")

        # Test Code Files Section
        test_frame = tk.LabelFrame(self, text="Test Code Files (space or newline separated)")
        test_frame.pack(fill="x", padx=5, pady=5)

        self.test_text = tk.Text(test_frame, height=5)
        self.test_text.pack(fill="x", padx=5, pady=5)

        test_buttons = tk.Frame(test_frame)
        test_buttons.pack(fill="x", padx=5, pady=5)

        tk.Button(test_buttons, text="Select Files",
                  command=lambda: self.select_files(self.test_text)).pack(side="left")
        tk.Button(test_buttons, text="Select Directory",
                  command=lambda: self.select_directory(self.test_text)).pack(side="left")

        # Prompt File Section
        prompt_frame = tk.LabelFrame(self, text="Prompt File (single file)")
        prompt_frame.pack(fill="x", padx=5, pady=5)

        self.prompt_entry = tk.Entry(prompt_frame)
        self.prompt_entry.pack(fill="x", padx=5, pady=5)

        tk.Button(prompt_frame, text="Select File",
                  command=self.select_prompt_file).pack(padx=5, pady=5)

        # Generate Button
        tk.Button(self, text="Generate JSON",
                  command=self.generate_json).pack(pady=10)

    def select_files(self, text_widget):
        files = filedialog.askopenfilenames()
        if files:
            current = text_widget.get("1.0", tk.END).strip()
            new_files = '\n'.join(files)
            if current:
                text_widget.insert(tk.END, '\n' + new_files)
            else:
                text_widget.insert(tk.END, new_files)

    def select_directory(self, text_widget):
        directory = filedialog.askdirectory()
        if directory:
            file_list = []
            for root_dir, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    file_list.append(file_path)

            current = text_widget.get("1.0", tk.END).strip()
            new_files = '\n'.join(file_list)
            if current:
                text_widget.insert(tk.END, '\n' + new_files)
            else:
                text_widget.insert(tk.END, new_files)

    def select_prompt_file(self):
        file = filedialog.askopenfilename()
        if file:
            self.prompt_entry.delete(0, tk.END)
            self.prompt_entry.insert(0, file)

    def generate_json(self):
        # Process source files
        source_content = self.source_text.get("1.0", tk.END)
        source_files = [line.strip() for line in source_content.splitlines() if line.strip()]

        # Process test files
        test_content = self.test_text.get("1.0", tk.END)
        test_files = [line.strip() for line in test_content.splitlines() if line.strip()]

        # Process prompt file
        prompt_file = self.prompt_entry.get().strip()

        # Create JSON structure
        config = {
            "source_code_files": {path: "" for path in source_files},
            "test_code_files": {path: "" for path in test_files},
            "prompt": prompt_file
        }

        # Save JSON file
        save_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )

        if save_path:
            try:
                with open(save_path, 'w') as f:
                    json.dump(config, f, indent=4)
                messagebox.showinfo("Success", f"Config saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("JSON Config Generator")
    root.geometry("600x600")
    app = Application(master=root)
    app.mainloop()