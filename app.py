import mysql.connector
from tkinter import *
from tkinter import messagebox

# Function to create a database and table if they don't exist
def create_database():
    # Connect to MySQL server (without specifying a database)
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="",  # Replace with your MySQL password
    )
    cursor = conn.cursor()

    # Create the database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS grade_calculator")
    conn.commit()

    # Connect to the newly created database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="",  # Replace with your MySQL password
        database="grade_calculator"  # Use the created database
    )
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_grades (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        father_name VARCHAR(255) NOT NULL,
        class VARCHAR(50) NOT NULL,
        book VARCHAR(255) NOT NULL,
        average FLOAT NOT NULL,
        grade VARCHAR(10) NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# Call the function to create the database and table
create_database()

# Tkinter GUI setup
win = Tk()
win.geometry("700x600")
win.title("Grade Calculator")

# Labels for results (initialized as empty)
total_label = Label(win, text="", font="impack 15 bold")
total_label.place(x=175, y=450)

average_label = Label(win, text="", font="impack 15 bold")
average_label.place(x=175, y=480)

grade_label = Label(win, text="", font="impack 15 bold")
grade_label.place(x=175, y=510)

def calculate():
    try:
        name = name_entry.get()
        father_name = father_name_entry.get()
        student_class = class_entry.get()
        book_name = book_entry.get()
        
        # Validation for name, father's name, class, and book
        if not name.strip() or not father_name.strip() or not student_class.strip() or not book_name.strip():
            messagebox.showerror("Invalid Input", "All fields must be filled.")
            return

        eng_marks = int(english_entry.get())
        pas_marks = int(pashto_entry.get())
        dar_marks = int(dari_entry.get())
        mat_marks = int(math_entry.get())
        scie_marks = int(science_entry.get())

        # Check if any marks are greater than 20
        if any(mark > 20 for mark in [eng_marks, pas_marks, dar_marks, mat_marks, scie_marks]):
            messagebox.showerror("Invalid Input", "Each subject should not have more than 20 marks.")
            return

        total = eng_marks + pas_marks + dar_marks + mat_marks + scie_marks
        max_total = 20 * 5  # Maximum possible total is 20 marks per subject for 5 subjects
        average = (total / max_total) * 100  # Scale the average to a percentage

        # Determine grade based on average
        if 90 <= average <= 100:
            grade = "A+"
        elif 80 <= average <= 89:
            grade = "A"
        elif 75 <= average <= 79:
            grade = "B+"
        elif 70 <= average <= 74:
            grade = "B"
        elif 65 <= average <= 69:
            grade = "C+"
        elif 60 <= average <= 64:
            grade = "C"
        else:
            grade = "FAIL"

        # Update the labels instead of creating new ones
        total_label.config(text=str(total))
        average_label.config(text=f"{average:.2f}%")
        grade_label.config(text=grade, fg="green" if grade != "FAIL" else "red")

        Label(win, text="Total", font="impack 13 bold").place(x=23, y=450)
        Label(win, text="Average", font="impack 13 bold").place(x=23, y=480)
        Label(win, text="Grade", font="impack 13 bold").place(x=23, y=510)

        # Insert data into MySQL database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="",  # Replace with your MySQL password
            database="grade_calculator"  # Use the created database
        )
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO student_grades (name, father_name, class, book, average, grade)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, father_name, student_class, book_name, average, grade))
        conn.commit()

        messagebox.showinfo("Success", "Data saved successfully!")
        conn.close()

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers for all subjects.")

def show_data():
    # Create a new window to show the data with a larger size
    show_window = Toplevel(win)
    show_window.geometry("900x600")  # Larger window size
    show_window.title("Student Data")

    # Create a table in the new window
    table = Frame(show_window)
    table.pack(fill=BOTH, expand=True)

    conn = mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="",  # Replace with your MySQL password
        database="grade_calculator"  # Use the created database
    )
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM student_grades")
    rows = cursor.fetchall()

    # Add column headers
    headers = ["ID", "Name", "Father's Name", "Class", "Book", "Average", "Grade"]
    for col, header in enumerate(headers):
        label = Label(table, text=header, font="Helvetica 10 bold", relief="solid", width=15)
        label.grid(row=0, column=col)

    # Add data rows
    for row_num, row in enumerate(rows, start=1):
        for col_num, value in enumerate(row):
            label = Label(table, text=value, font="Helvetica 10", relief="solid", width=15)
            label.grid(row=row_num, column=col_num)

    conn.close()

# Function to delete a student record (Search by Name or ID)
def delete_student():
    def search_student():
        search_input = search_entry.get()
        
        # Determine if the input is a number (ID) or a string (Name)
        try:
            student_id = int(search_input)
            query = "SELECT * FROM student_grades WHERE id = %s"
            params = (student_id,)
        except ValueError:
            student_id = None
            query = "SELECT * FROM student_grades WHERE name = %s"
            params = (search_input,)

        conn = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="",  # Replace with your MySQL password
            database="grade_calculator"
        )
        cursor = conn.cursor()
        cursor.execute(query, params)
        student = cursor.fetchone()
        conn.close()

        if student:
            details_label.config(text=f"Name: {student[1]}\nFather's Name: {student[2]}\nClass: {student[3]}\nBook: {student[4]}\nAverage: {student[5]}\nGrade: {student[6]}")
            delete_button.config(state=NORMAL)
        else:
            messagebox.showinfo("Not Found", "No student found with that ID or Name.")
            details_label.config(text="")
            delete_button.config(state=DISABLED)

    def confirm_delete():
        search_input = search_entry.get()

        # Determine if the input is a number (ID) or a string (Name)
        try:
            student_id = int(search_input)
            query = "DELETE FROM student_grades WHERE id = %s"
            params = (student_id,)
        except ValueError:
            student_id = None
            query = "DELETE FROM student_grades WHERE name = %s"
            params = (search_input,)

        conn = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="",  # Replace with your MySQL password
            database="grade_calculator"
        )
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Student record deleted successfully.")
        delete_window.destroy()

    delete_window = Toplevel(win)
    delete_window.geometry("400x300")
    delete_window.title("Delete Student")

    Label(delete_window, text="Enter Student's Name or ID:", font="Helvetica 12").pack(pady=10)
    search_entry = Entry(delete_window, font="Helvetica 12", width=30)
    search_entry.pack(pady=5)
    search_button = Button(delete_window, text="Search", font="Helvetica 12", command=search_student)
    search_button.pack(pady=10)

    details_label = Label(delete_window, text="", font="Helvetica 12")
    details_label.pack(pady=10)

    delete_button = Button(delete_window, text="Delete", font="Helvetica 12", state=DISABLED, command=confirm_delete)
    delete_button.pack(pady=10)

# Header section
Label(win, text="Grade Calculator", font="impact 20 bold", bg="black", fg="white").pack(fill=X)

# Student details section
Label(win, text="Name", font="23").place(x=23, y=40)
Label(win, text="F/Name", font="23").place(x=23, y=70)
Label(win, text="Class", font="23").place(x=23, y=100)
Label(win, text="Book", font="23").place(x=23, y=130)

name_entry = Entry(win, font=20, width=20, bd=2)
name_entry.place(x=150, y=40)

father_name_entry = Entry(win, font=20, width=20, bd=2)
father_name_entry.place(x=150, y=70)

class_entry = Entry(win, font=20, width=20, bd=2)
class_entry.place(x=150, y=100)

book_entry = Entry(win, font=20, width=20, bd=2)
book_entry.place(x=150, y=130)

# Marks entry section
Label(win, text="Grammar", font="23").place(x=23, y=180)
Label(win, text="Speaking", font="23").place(x=23, y=215)
Label(win, text="Reading", font="23").place(x=23, y=250)
Label(win, text="Writing", font="23").place(x=23, y=285)
Label(win, text="Listening", font="23").place(x=23, y=320)

english_entry = Entry(win, font=20, width=15, bd=2)
english_entry.place(x=150, y=180)

pashto_entry = Entry(win, font=20, width=15, bd=2)
pashto_entry.place(x=150, y=215)

dari_entry = Entry(win, font=20, width=15, bd=2)
dari_entry.place(x=150, y=250)

math_entry = Entry(win, font=20, width=15, bd=2)
math_entry.place(x=150, y=285)

science_entry = Entry(win, font=20, width=15, bd=2)
science_entry.place(x=150, y=320)


# Buttons
Button(win, text="Calculate", font="impack 15 bold", bg="blue", fg="white", command=calculate).place(x=80, y=540)
Button(win, text="Exit", font="impack 15 bold", bg="red", fg="white", width=8, command=lambda: exit()).place(x=210, y=540)
Button(win, text="Show Data", font="impack 15 bold", bg="green", fg="white", command=show_data).place(x=350, y=540)
Button(win, text="Delete Student", font="impack 15 bold", bg="red", fg="white", command=delete_student).place(x=500, y=540)

mainloop()