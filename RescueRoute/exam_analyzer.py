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
class Person:
  """Base class representing a person in the institution"""

  def __init__(self, roll_no, name):
    self.roll_no = roll_no
    self.name = name

  def get_details(self):
    return f"Roll No: {self.roll_no}, Name: {self.name}"


class Student(Person):
  """Subclass representing a student with exam marks"""

  def __init__(self, roll_no, name, maths, science, english):
    super().__init__(roll_no, name)
    self.maths = maths
    self.science = science
    self.english = english

  def calculate_total(self):
    scores = [self.maths, self.science, self.english]
    valid_scores = [s for s in scores if not np.isnan(s)]
    return sum(valid_scores)

  def assign_grade(self, total_marks):
    avg = total_marks / 3.0
    if avg >= 85:
      return "Grade A"
    elif avg >= 70:
      return "Grade B"
    elif avg >= 50:
      return "Grade C"
    elif avg >= 35:
      return "Grade D"
    else:
      return "Fail"


# ==========================================
# 2. Main GUI Application Class (Unit 3)
# ==========================================
class ExamAnalyzerApp:

  def __init__(self, root):
    self.root = root
    self.root.title(
        "University Examination Result Analyzer & Grade Distribution Tool"
    )
    self.root.geometry("950x720")
    self.root.config(bg="#f4f6f9")

    # Initial Mock Dataset with some missing values (NaN) for data cleaning demo
    self.raw_data = [
        {"RollNo": 101, "Name": "Rahul Sharma", "Maths": 85, "Science": 90, "English": 78},
        {"RollNo": 102, "Name": "Priya Verma", "Maths": 92, "Science": np.nan, "English": 88},
        {"RollNo": 103, "Name": "Amit Kumar", "Maths": 45, "Science": 50, "English": 40},
        {"RollNo": 104, "Name": "Neha Singh", "Maths": 76, "Science": 82, "English": np.nan},
        {"RollNo": 105, "Name": "Rohan Das", "Maths": 30, "Science": 35, "English": 32},
    ]

    self.create_widgets()

  def create_widgets(self):
    # Title Header
    title_label = tk.Label(
        self.root,
        text="University Examination Result & Grade Analyzer",
        font=("Arial", 16, "bold"),
        bg="#1b4f72",
        fg="white",
        pady=10,
    )
    title_label.pack(fill=tk.X)

    # --- Form Frame to Add New Student Live ---
    form_frame = tk.LabelFrame(
        self.root,
        text=" Add New Student Record ",
        font=("Arial", 10, "bold"),
        bg="#f4f6f9",
        fg="#2c3e50",
        padx=15,
        pady=10,
    )
    form_frame.pack(fill=tk.X, padx=20, pady=10)

    tk.Label(form_frame, text="Roll No:", bg="#f4f6f9").grid(
        row=0, column=0, padx=5, sticky="w"
    )
    self.ent_roll = tk.Entry(form_frame, width=8)
    self.ent_roll.grid(row=0, column=1, padx=5)

    tk.Label(form_frame, text="Name:", bg="#f4f6f9").grid(
        row=0, column=2, padx=5, sticky="w"
    )
    self.ent_name = tk.Entry(form_frame, width=15)
    self.ent_name.grid(row=0, column=3, padx=5)

    tk.Label(form_frame, text="Maths:", bg="#f4f6f9").grid(
        row=0, column=4, padx=5, sticky="w"
    )
    self.ent_maths = tk.Entry(form_frame, width=6)
    self.ent_maths.grid(row=0, column=5, padx=5)

    tk.Label(form_frame, text="Science:", bg="#f4f6f9").grid(
        row=0, column=6, padx=5, sticky="w"
    )
    self.ent_science = tk.Entry(form_frame, width=6)
    self.ent_science.grid(row=0, column=7, padx=5)

    tk.Label(form_frame, text="English:", bg="#f4f6f9").grid(
        row=0, column=8, padx=5, sticky="w"
    )
    self.ent_english = tk.Entry(form_frame, width=6)
    self.ent_english.grid(row=0, column=9, padx=5)

    btn_add = tk.Button(
        form_frame,
        text="Add Student",
        command=self.add_student,
        bg="#2980b9",
        fg="white",
        font=("Arial", 9, "bold"),
        padx=8,
    )
    btn_add.grid(row=0, column=10, padx=15)

    # --- Action Buttons Frame for Analytics & Charts ---
    btn_frame = tk.Frame(self.root, bg="#f4f6f9", pady=5)
    btn_frame.pack()

    tk.Button(
        btn_frame,
        text="View Analytics Summary",
        command=self.show_analytics_summary,
        bg="#27ae60",
        fg="white",
        font=("Arial", 9, "bold"),
        padx=8,
        pady=4,
    ).grid(row=0, column=0, padx=6)
    tk.Button(
        btn_frame,
        text="Subject Averages (Bar)",
        command=self.plot_subject_averages,
        bg="#3498db",
        fg="white",
        font=("Arial", 9, "bold"),
        padx=8,
        pady=4,
    ).grid(row=0, column=1, padx=6)
    tk.Button(
        btn_frame,
        text="Grade Distribution (Pie)",
        command=self.plot_grade_distribution,
        bg="#8e44ad",
        fg="white",
        font=("Arial", 9, "bold"),
        padx=8,
        pady=4,
    ).grid(row=0, column=2, padx=6)
    tk.Button(
        btn_frame,
        text="Score Spread (Histogram)",
        command=self.plot_score_histogram,
        bg="#d35400",
        fg="white",
        font=("Arial", 9, "bold"),
        padx=8,
        pady=4,
    ).grid(row=0, column=3, padx=6)

    # --- Table View Frame (ttk.Treeview) ---
    table_frame = tk.Frame(self.root)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    self.tree = ttk.Treeview(
        table_frame,
        columns=("RollNo", "Name", "Maths", "Science", "English", "Total", "Grade"),
        show="headings",
    )
    self.tree.heading("RollNo", text="Roll No")
    self.tree.heading("Name", text="Student Name")
    self.tree.heading("Maths", text="Maths (100)")
    self.tree.heading("Science", text="Science (100)")
    self.tree.heading("English", text="English (100)")
    self.tree.heading("Total", text="Total (300)")
    self.tree.heading("Grade", text="Final Grade")
    
    self.tree.pack(fill=tk.BOTH, expand=True)

    self.load_table_data()

    # Footer
    footer = tk.Label(
        self.root,
        text="MCA AI/ML Python Project - Syllabus Aligned (OOP + NumPy/Pandas + Matplotlib/Seaborn + Tkinter)",
        font=("Arial", 9, "italic"),
        bg="#f4f6f9",
        fg="#7f8c8d",
        pady=6,
    )
    footer.pack(fill=tk.X)

  def add_student(self):
    """Function to dynamically add a student record from the GUI form"""
    try:
      r_no = int(self.ent_roll.get())
      name = self.ent_name.get().strip()
      if not name:
        raise ValueError("Name cannot be empty")

      # If a mark field is left empty, treat it as NaN to test imputation
      maths = float(self.ent_maths.get()) if self.ent_maths.get().strip() else np.nan
      science = float(self.ent_science.get()) if self.ent_science.get().strip() else np.nan
      english = float(self.ent_english.get()) if self.ent_english.get().strip() else np.nan

      self.raw_data.append(
          {"RollNo": r_no, "Name": name, "Maths": maths, "Science": science, "English": english}
      )
      self.load_table_data()

      # Clear input fields
      self.ent_roll.delete(0, tk.END)
      self.ent_name.delete(0, tk.END)
      self.ent_maths.delete(0, tk.END)
      self.ent_science.delete(0, tk.END)
      self.ent_english.delete(0, tk.END)

      messagebox.showinfo("Success", "New student record added successfully!")
    except Exception as e:
      messagebox.showerror("Input Error", f"Please check your inputs: {e}")

  def get_cleaned_dataframe(self):
    """Data Analytics: Pandas cleaning & median imputation"""
    df = pd.DataFrame(self.raw_data)
    for col in ["Maths", "Science", "English"]:
      median_val = df[col].median()
      df[col] = df[col].fillna(median_val)
      
    totals, grades = [], []
    for _, row in df.iterrows():
      student = Student(row["RollNo"], row["Name"], row["Maths"], row["Science"], row["English"])
      tot = student.calculate_total()
      grd = student.assign_grade(tot)
      totals.append(tot)
      grades.append(grd)
      
    df["Total"] = totals
    df["Grade"] = grades
    return df

  def load_table_data(self):
    for item in self.tree.get_children():
      self.tree.delete(item)

    df = self.get_cleaned_dataframe()
    for _, row in df.iterrows():
      self.tree.insert(
          "",
          tk.END,
          values=(
              int(row["RollNo"]),
              row["Name"],
              round(row["Maths"], 1),
              round(row["Science"], 1),
              round(row["English"], 1),
              round(row["Total"], 1),
              row["Grade"],
          ),
      )

  def show_analytics_summary(self):
    df = self.get_cleaned_dataframe()
    avg_total = df["Total"].mean()
    highest_scorer = df.loc[df["Total"].idxmax()]["Name"]
    
    msg = (
        f"Data Analytics & Imputation Complete!\n\n"
        f"Total Students Evaluated: {len(df)}\n"
        f"Missing Marks Imputed with Subject Medians.\n"
        f"Class Average Total Score: {avg_total:.2f} / 300\n"
        f"Top Performing Student: {highest_scorer}"
    )
    messagebox.showinfo("Examination Analytics Summary", msg)
    self.load_table_data()

  def plot_subject_averages(self):
    df = self.get_cleaned_dataframe()
    subj_means = [df["Maths"].mean(), df["Science"].mean(), df["English"].mean()]
    subjects = ["Maths", "Science", "English"]

    plt.figure(figsize=(6, 4))
    plt.bar(subjects, subj_means, color=["#3498db", "#2ecc71", "#e67e22"], width=0.4)
    plt.title("Average Scores by Subject", fontsize=12, fontweight="bold")
    plt.ylabel("Average Marks (out of 100)")
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.show()

  def plot_grade_distribution(self):
    df = self.get_cleaned_dataframe()
    grade_counts = df["Grade"].value_counts()

    plt.figure(figsize=(6, 6))
    plt.pie(
        grade_counts,
        labels=grade_counts.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=["#2ecc71", "#3498db", "#f1c40f", "#e74c3c"],
    )
    plt.title("Student Grade Distribution", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.show()

  def plot_score_histogram(self):
    df = self.get_cleaned_dataframe()

    plt.figure(figsize=(6, 4))
    sns.histplot(df["Total"], bins=5, kde=True, color="#8e44ad")
    plt.title("Distribution of Total Exam Scores", fontsize=12, fontweight="bold")
    plt.xlabel("Total Marks (out of 300)")
    plt.ylabel("Number of Students")
    plt.tight_layout()
    plt.show()


# ==========================================
# Execution Entry Point
# ==========================================
if __name__ == "__main__":
  root = tk.Tk()
  app = ExamAnalyzerApp(root)
  root.mainloop()










import tkinter as tk
def left_click(event):
  print("Left mouse button clicked!")
window = tk.Tk()
button=tk.button(window, text="Click Me")
button.pack()
button.bind("<Button-1>", left_click)
window.mainloop()


import tkinter as tk
def right_click(event):
  print("Right mouse button clicked!")
window = tk.Tk()
button=tk.button(window, text="Click Me")
button.pack()
button.bind("<Button-2>", right_click)
window.mainloop()



import tkinter as tk
def double_click(event):
  print("Button was double-clicked!")
window=tk.Tk()
button=tk.Button(window, text="Double Click Me")
button.pack()
button.bind("<Double-Button-1", double_click)
window.mainloop()