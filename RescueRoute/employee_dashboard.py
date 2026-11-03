import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set visual style for plots
sns.set_theme(style="whitegrid")


# ==========================================
# 1. OOP: Classes and Inheritance (Unit 1 & 2)
# ==========================================
class Employee:

  def __init__(self, emp_id, name, department, base_salary, performance_score):
    self.emp_id = emp_id
    self.name = name
    self.department = department
    self.base_salary = base_salary
    self.performance_score = performance_score

  def calculate_total_compensation(self):
    return self.base_salary


class FullTimeEmployee(Employee):

  def __init__(
      self, emp_id, name, department, base_salary, performance_score, bonus
  ):
    super().__init__(emp_id, name, department, base_salary, performance_score)
    self.bonus = bonus

  def calculate_total_compensation(self):
    # Bonus scales with performance score (1 to 5)
    return self.base_salary + (self.bonus * (self.performance_score / 5.0))


class ContractEmployee(Employee):

  def __init__(
      self,
      emp_id,
      name,
      department,
      base_salary,
      performance_score,
      project_allowance,
  ):
    super().__init__(emp_id, name, department, base_salary, performance_score)
    self.project_allowance = project_allowance

  def calculate_total_compensation(self):
    return self.base_salary + self.project_allowance


# ==========================================
# 2. Main GUI Application Class (Unit 3)
# ==========================================
class EmployeeDashboardApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Smart Employee Performance & Salary Analytics Dashboard")
    self.root.geometry("850x650")
    self.root.config(bg="#f4f6f9")

    # Initial Mock Dataset (Simulating database/CSV)
    self.employees_data = [
        {"ID": 101, "Name": "Alice Smith", "Dept": "Sales", "Salary": 50000, "Perf": 4, "Type": "FullTime"},
        {"ID": 102, "Name": "Bob Jones", "Dept": "Engineering", "Salary": 80000, "Perf": 5, "Type": "FullTime"},
        {"ID": 103, "Name": "Charlie Brown", "Dept": "Sales", "Salary": np.nan, "Perf": 3, "Type": "FullTime"},  # Missing data for testing
        {"ID": 104, "Name": "Diana Prince", "Dept": "HR", "Salary": 45000, "Perf": 4, "Type": "Contract"},
        {"ID": 105, "Name": "Evan Wright", "Dept": "Engineering", "Salary": 75000, "Perf": 2, "Type": "Contract"},
        {"ID": 106, "Name": "Fiona Gallagher", "Dept": "Sales", "Salary": 55000, "Perf": 5, "Type": "FullTime"},
        {"ID": 107, "Name": "George Clark", "Dept": "HR", "Salary": np.nan, "Perf": 3, "Type": "Contract"},  # Missing data
    ]

    self.create_widgets()

  def create_widgets(self):
    # Title Header
    title_label = tk.Label(
        self.root,
        text="Employee Performance & Salary Analytics",
        font=("Arial", 16, "bold"),
        bg="#2c3e50",
        fg="white",
        pady=10,
    )
    title_label.pack(fill=tk.X)

    # Frame for Action Buttons (Using Grid & Pack geometry managers as required by syllabus)
    btn_frame = tk.Frame(self.root, bg="#f4f6f9", pady=15)
    btn_frame.pack()

    # Button 1: View Data and Clean Missing Values (Pandas)
    btn_view = tk.Button(
        btn_frame,
        text="View Cleaned Data Summary",
        command=self.show_data_summary,
        bg="#3498db",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=10,
        pady=5,
    )
    btn_view.grid(row=0, column=0, padx=10)

    # Button 2: Department Salary Bar Chart (Matplotlib)
    btn_bar = tk.Button(
        btn_frame,
        text="Dept Average Salary (Bar)",
        command=self.plot_dept_salary,
        bg="#2ecc71",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=10,
        pady=5,
    )
    btn_bar.grid(row=0, column=1, padx=10)

    # Button 3: Performance vs Salary Scatter Plot (Seaborn)
    btn_scatter = tk.Button(
        btn_frame,
        text="Perf vs Salary (Scatter)",
        command=self.plot_perf_vs_salary,
        bg="#e67e22",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=10,
        pady=5,
    )
    btn_scatter.grid(row=0, column=2, padx=10)

    # Button 4: Department Share Pie Chart
    btn_pie = tk.Button(
        btn_frame,
        text="Dept Headcount (Pie)",
        command=self.plot_dept_pie,
        bg="#9b59b6",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=10,
        pady=5,
    )
    btn_pie.grid(row=0, column=3, padx=10)

    # Frame for Table View (Treeview) to display employee records inside Tkinter
    table_frame = tk.Frame(self.root)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    self.tree = ttk.Treeview(
        table_frame, columns=("ID", "Name", "Dept", "Salary", "Perf", "Type"), show="headings"
    )
    self.tree.heading("ID", text="Emp ID")
    self.tree.heading("Name", text="Employee Name")
    self.tree.heading("Dept", text="Department")
    self.tree.heading("Salary", text="Base Salary")
    self.tree.heading("Perf", text="Performance (1-5)")
    self.tree.heading("Type", text="Emp Type")
    
    self.tree.pack(fill=tk.BOTH, expand=True)

    # Load initial data into Treeview
    self.load_treeview_data()

    # Footer status
    footer = tk.Label(
        self.root,
        text="MCA Python Project - Syllabus Aligned (OOP + NumPy/Pandas + Matplotlib + Tkinter)",
        font=("Arial", 9, "italic"),
        bg="#f4f6f9",
        fg="#7f8c8d",
        pady=5,
    )
    footer.pack(fill=tk.X)

  def get_processed_dataframe(self):
    """Data Analytics using Pandas & NumPy (Experiment 4 style cleaning)"""
    df = pd.DataFrame(self.employees_data)
    
    # Handle missing values by filling Salary with the median salary of the department/dataset
    median_salary = df["Salary"].median()
    df["Salary"] = df["Salary"].fillna(median_salary)
    
    return df

  def load_treeview_data(self):
    # Clear existing items
    for item in self.tree.get_children():
      self.tree.delete(item)
      
    df = self.get_processed_dataframe()
    for index, row in df.iterrows():
      self.tree.insert(
          "",
          tk.END,
          values=(
              row["ID"],
              row["Name"],
              row["Dept"],
              f"₹{row['Salary']:,.2f}",
              row["Perf"],
              row["Type"],
          ),
      )

  def show_data_summary(self):
    df = self.get_processed_dataframe()
    avg_sales_salary = df[df["Dept"] == "Sales"]["Salary"].mean()
    
    summary_text = (
        f"Data Analysis Complete via Pandas!\n\n"
        f"Total Employees: {len(df)}\n"
        f"Missing Salaries Imputed with Median: ₹{df['Salary'].median():,.2f}\n"
        f"Average Salary in 'Sales' Dept: ₹{avg_sales_salary:,.2f}"
    )
    messagebox.showinfo("Pandas Analytics Summary", summary_text)
    self.load_treeview_data()  # Refresh table to show imputed values

  def plot_dept_salary(self):
    """Matplotlib Bar Plot: Average Salary by Department"""
    df = self.get_processed_dataframe()
    dept_salary = df.groupby("Dept")["Salary"].mean().reset_index()

    plt.figure(figsize=(7, 4))
    plt.bar(dept_salary["Dept"], dept_salary["Salary"], color="#3498db", width=0.5)
    plt.title("Average Salary by Department", fontsize=12, fontweight="bold")
    plt.xlabel("Department", fontsize=10)
    plt.ylabel("Average Salary (₹)", fontsize=10)
    plt.tight_layout()
    plt.show()

  def plot_perf_vs_salary(self):
    """Seaborn Scatter Plot: Performance Score vs Salary"""
    df = self.get_processed_dataframe()

    plt.figure(figsize=(7, 4))
    sns.scatterplot(
        data=df,
        x="Perf",
        y="Salary",
        hue="Dept",
        style="Type",
        s=100,
        palette="deep",
    )
    plt.title("Correlation: Performance Score vs Salary", fontsize=12, fontweight="bold")
    plt.xlabel("Performance Score (1-5)", fontsize=10)
    plt.ylabel("Salary (₹)", fontsize=10)
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.show()

  def plot_dept_pie(self):
    """Matplotlib Pie Chart: Department Headcount Distribution"""
    df = self.get_processed_dataframe()
    dept_counts = df["Dept"].value_counts()

    plt.figure(figsize=(6, 6))
    plt.pie(
        dept_counts,
        labels=dept_counts.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=["#ff9999", "#66b3ff", "#99ff99"],
    )
    plt.title("Employee Distribution by Department", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.show()


# ==========================================
# Main Execution Entry Point
# ==========================================
if __name__ == "__main__":
  root = tk.Tk()
  app = EmployeeDashboardApp(root)
  root.mainloop()