import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from fractions import Fraction

# --------------------------------------------------------------
# IMPORTANT: Install once with: pip install ttkthemes
# --------------------------------------------------------------
from ttkthemes import ThemedStyle   # <-- This gives us beautiful themes

# --- Solver Logic (unchanged) ---
class LinearSystemSolver:
    def __init__(self, log_callback):
        self.log_callback = log_callback

    def log(self, message=""):
        self.log_callback(str(message) + "\n")

    def format_value(self, x):
        if x.denominator == 1:
            return str(x.numerator)
        return f"{x.numerator}/{x.denominator}"

    def print_matrix(self, matrix, title="Current Matrix State"):
        rows = len(matrix)
        self.log(f"\n--- {title} ---")
        for row in matrix:
            formatted_row = [self.format_value(x) for x in row]
            self.log(f" [{', '.join(f'{val:>8}' for val in formatted_row)}]")
        self.log("-" * 40)

    def solve(self, coefficients, constants):
        rows = len(coefficients)
        if rows == 0:
            return
        matrix = []
        for i in range(rows):
            row_copy = [Fraction(x).limit_denominator() for x in coefficients[i]] + [Fraction(constants[i]).limit_denominator()]
            matrix.append(row_copy)
        cols = len(matrix[0])
        n_vars = cols - 1
        self.log("INITIAL SYSTEM:")
        self.print_matrix(matrix, "Augmented Matrix")
        self.log("\n=== PHASE 1: ROW ECHELON FORM (Gaussian Elimination) ===")
       
        pivot_row = 0
        for col in range(n_vars):
            if pivot_row >= rows:
                break
            pivot_val = matrix[pivot_row][col]
            if pivot_val == 0:
                self.log(f"Pivot at R{pivot_row+1}, C{col+1} is zero. Swapping disabled, skipping column.")
                continue
            if pivot_val != 1:
                self.log(f"OPERATION: R{pivot_row+1} <--- R{pivot_row+1} / ({self.format_value(pivot_val)})")
                matrix[pivot_row] = [x / pivot_val for x in matrix[pivot_row]]
                self.print_matrix(matrix)
           
            for r in range(pivot_row + 1, rows):
                factor = matrix[r][col]
                if factor != 0:
                    self.log(f"OPERATION: R{r+1} <--- R{r+1} - ({self.format_value(factor)} * R{pivot_row+1})")
                    new_row = [matrix[r][c_idx] - (factor * matrix[pivot_row][c_idx]) for c_idx in range(cols)]
                    matrix[r] = new_row
                    self.print_matrix(matrix)
            pivot_row += 1
        self.log("\n>>> Matrix is now in Row Echelon Form (REF).")
       
        self.log("\n=== PHASE 2: REDUCED ROW ECHELON FORM (Back Substitution) ===")
       
        for i in range(rows - 1, -1, -1):
            pivot_col = -1
            for c in range(n_vars):
                if matrix[i][c] == 1:
                    pivot_col = c
                    break
            if pivot_col == -1:
                continue
            for r in range(i - 1, -1, -1):
                factor = matrix[r][pivot_col]
                if factor != 0:
                    self.log(f"OPERATION: R{r+1} <--- R{r+1} - ({self.format_value(factor)} * R{i+1})")
                    new_row = [matrix[r][c_idx] - (factor * matrix[i][c_idx]) for c_idx in range(cols)]
                    matrix[r] = new_row
                    self.print_matrix(matrix)
        self.log("\n>>> Matrix is now in Reduced Row Echelon Form (RREF).")
       
        self.log("\n=== FINAL SOLUTION ===")
        solutions = []
        for i in range(rows):
            is_all_zeros = all(x == 0 for x in matrix[i][:-1])
            constant = matrix[i][-1]
            if is_all_zeros and constant != 0:
                self.log("System is INCONSISTENT (No Solution).")
                return
            elif is_all_zeros and constant == 0:
                continue
            else:
                solutions.append(constant)
        if solutions:
            for idx, val in enumerate(solutions):
                self.log(f"x{idx+1} = {self.format_value(val)}")
        else:
            self.log("Infinite solutions or trivial system.")


# --- GUI Application (DARK MODERN THEME - SAME SIZE) ---
class SolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Linear System Solver • Dark Edition")
        self.root.geometry("950x800")
        self.root.configure(bg="#1e1e1e")   # Dark background

        # === Apply beautiful dark theme ===
        style = ThemedStyle(root)
        style.set_theme("equilux")          # One of the best dark themes (or try "arc", "black", "yaru")

        # Optional: fine-tune colors if needed
        style.configure(".", background="#1e1e1e", foreground="#d4d4d4", font=("Segoe UI", 10))
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff")
        style.configure("TLabelframe", background="#1e1e1e", foreground="#00ff99")
        style.configure("TLabelframe.Label", foreground="#00ff99", font=("Segoe UI", 11, "bold"))
        style.configure("TButton", padding=8, font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", "#005f40")])
        style.configure("Treeview", background="#2d2d2d", fieldbackground="#2d2d2d", foreground="white")

        # --- Configuration ---
        config_frame = ttk.LabelFrame(root, text="Configuration", padding="12")
        config_frame.pack(fill="x", padx=12, pady=8)

        ttk.Label(config_frame, text="Rows:").pack(side="left", padx=5)
        self.rows_var = tk.StringVar(value="3")
        ttk.Entry(config_frame, textvariable=self.rows_var, width=6).pack(side="left", padx=5)
        ttk.Label(config_frame, text="Total Columns:").pack(side="left", padx=(20,5))
        self.cols_var = tk.StringVar(value="4")
        ttk.Entry(config_frame, textvariable=self.cols_var, width=6).pack(side="left", padx=5)
        ttk.Button(config_frame, text="Generate Grid", command=self.create_grid).pack(side="left", padx=25)

        # --- Matrix Frame ---
        self.matrix_frame = ttk.LabelFrame(root, text="Augmented Matrix Input (last column = constants)", padding="10")
        self.matrix_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.canvas = tk.Canvas(self.matrix_frame, bg="#1e1e1e", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.matrix_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.entries = []

        placeholder = ttk.Label(self.scrollable_frame,
                                text="Set rows & columns above → Generate Grid",
                                font=("Segoe UI", 12, "italic"), foreground="#888888")
        placeholder.pack(pady=50)

        # --- Bottom Controls & Output ---
        bottom_frame = ttk.Frame(root, padding="10")
        bottom_frame.pack(fill="both", expand=True, padx=12, pady=8)

        solve_btn = ttk.Button(bottom_frame, text="SOLVE SYSTEM", command=self.solve_gui)
        solve_btn.pack(fill="x", pady=(0, 10))

        ttk.Label(bottom_frame, text="Step-by-Step Solution Log:", font=("Segoe UI", 11, "bold"), foreground="#00ff99").pack(anchor="w")

        self.output_text = scrolledtext.ScrolledText(
            bottom_frame,
            height=28,
            state='disabled',
            font=("Consolas", 11),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#00ff99",
            selectbackground="#004d33",
            relief="flat",
            bd=4
        )
        self.output_text.pack(fill="both", expand=True)

    def create_grid(self):
        try:
            rows = int(self.rows_var.get())
            total_cols = int(self.cols_var.get())
            if rows < 1 or total_cols < 2:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Rows ≥ 1, Total columns ≥ 2")
            return

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.entries = []

        for i in range(rows):
            row_entries = []
            for j in range(total_cols):
                entry = ttk.Entry(self.scrollable_frame, width=11, justify="center", font=("Consolas", 11))
                entry.grid(row=i, column=j, padx=6, pady=6)
                entry.insert(0, "0")
                row_entries.append(entry)
            self.entries.append(row_entries)

        if self.entries:
            self.entries[0][0].focus_set()

    def append_log(self, text):
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')

    def solve_gui(self):
        if not self.entries:
            messagebox.showwarning("No Matrix", "Generate the grid first.")
            return

        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')

        try:
            coefficients = []
            constants = []
            for row in self.entries:
                values = [Fraction(e.get().strip() or "0") for e in row]
                coefficients.append(values[:-1])
                constants.append(values[-1])

            solver = LinearSystemSolver(self.append_log)
            solver.solve(coefficients, constants)
        except Exception as e:
            messagebox.showerror("Input Error", "Please enter valid numbers or fractions.\nDetails: " + str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = SolverApp(root)
    root.mainloop()