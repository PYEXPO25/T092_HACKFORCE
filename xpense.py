import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from PIL import Image
import pytesseract
import csv
import matplotlib.pyplot as plt
import re

# Set path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class ExpenseTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("1300x600")
        self.expenses = []
        self.categories = [
            "Food", "Transportation", "Utilities", "Entertainment", "Other"
        ]
        self.category_var = tk.StringVar(self)
        self.category_var.set(self.categories[0])
        self.currencies = ["USD", "EUR", "GBP", "JPY", "INR"]
        self.currency_var = tk.StringVar(self)
        self.currency_var.set(self.currencies[0])
        self.create_widgets()
        self.load_expenses()

    def create_widgets(self):
        # Title Label
        self.label = tk.Label(self, text="Expense Tracker", font=("Helvetica", 20, "bold"))
        self.label.pack(pady=10)

        # Input frame for adding expenses
        self.frame_input = tk.Frame(self)
        self.frame_input.pack(pady=10)

        # Expense amount input
        self.expense_label = tk.Label(self.frame_input, text="Expense Amount:", font=("Helvetica", 12))
        self.expense_label.grid(row=0, column=0, padx=5)
        self.expense_entry = tk.Entry(self.frame_input, font=("Helvetica", 12), width=15)
        self.expense_entry.grid(row=0, column=1, padx=5)

        # Item description input
        self.item_label = tk.Label(self.frame_input, text="Item Description:", font=("Helvetica", 12))
        self.item_label.grid(row=0, column=2, padx=5)
        self.item_entry = tk.Entry(self.frame_input, font=("Helvetica", 12), width=20)
        self.item_entry.grid(row=0, column=3, padx=5)

        # Category dropdown
        self.category_label = tk.Label(self.frame_input, text="Category:", font=("Helvetica", 12))
        self.category_label.grid(row=0, column=4, padx=5)
        self.category_dropdown = ttk.Combobox(self.frame_input, textvariable=self.category_var, values=self.categories, font=("Helvetica", 12), width=15)
        self.category_dropdown.grid(row=0, column=5, padx=5)

        # Currency dropdown
        self.currency_label = tk.Label(self.frame_input, text="Currency:", font=("Helvetica", 12))
        self.currency_label.grid(row=0, column=6, padx=5)
        self.currency_dropdown = ttk.Combobox(self.frame_input, textvariable=self.currency_var, values=self.currencies, font=("Helvetica", 12), width=10)
        self.currency_dropdown.grid(row=0, column=7, padx=5)

        # Date input
        self.date_label = tk.Label(self.frame_input, text="Date (YYYY-MM-DD):", font=("Helvetica", 12))
        self.date_label.grid(row=0, column=8, padx=5)
        self.date_entry = tk.Entry(self.frame_input, font=("Helvetica", 12), width=15)
        self.date_entry.grid(row=0, column=9, padx=5)

        # Add Expense Button
        self.add_button = tk.Button(self, text="Add Expense", command=self.add_expense)
        self.add_button.pack(pady=5)

        # Expense Listbox
        self.frame_list = tk.Frame(self)
        self.frame_list.pack(pady=10)
        self.scrollbar = tk.Scrollbar(self.frame_list)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.expense_listbox = tk.Listbox(self.frame_list, font=("Helvetica", 12), width=70, yscrollcommand=self.scrollbar.set)
        self.expense_listbox.pack(pady=5)
        self.scrollbar.config(command=self.expense_listbox.yview)

        # Buttons for editing, deleting, saving
        self.edit_button = tk.Button(self, text="Edit Expense", command=self.edit_expense)
        self.edit_button.pack(pady=5)
        self.delete_button = tk.Button(self, text="Delete Expense", command=self.delete_expense)
        self.delete_button.pack(pady=5)
        self.save_button = tk.Button(self, text="Save Expenses", command=self.save_expenses)
        self.save_button.pack(pady=5)

        # Total Expense Label
        self.total_label = tk.Label(self, text="Total Expenses:", font=("Helvetica", 12))
        self.total_label.pack(pady=5)

        # Show Expenses Chart Button
        self.show_chart_button = tk.Button(self, text="Show Expenses Chart", command=self.show_expenses_chart)
        self.show_chart_button.pack(pady=5)

        # OCR Button
        self.ocr_button = tk.Button(self, text="Extract Text from Receipt (OCR)", command=self.extract_text_from_image)
        self.ocr_button.pack(pady=5)

        self.update_total_label()

    def add_expense(self):
        expense = self.expense_entry.get()
        item = self.item_entry.get()
        category = self.category_var.get()
        currency = self.currency_var.get()
        date = self.date_entry.get()
        if expense and date:
            self.expenses.append((expense, item, category, currency, date))
            self.expense_listbox.insert(tk.END, f"{expense} - {item} - {category} - {currency} ({date})")
            self.expense_entry.delete(0, tk.END)
            self.item_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Expense and Date cannot be empty.")
        self.update_total_label()

    def edit_expense(self):
        selected_index = self.expense_listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]
            selected_expense = self.expenses[selected_index]
            new_expense = simpledialog.askstring("Edit Expense", "Enter new expense:", initialvalue=selected_expense[0])
            new_item = simpledialog.askstring("Edit Item", "Enter new item description:", initialvalue=selected_expense[1])
            new_category = simpledialog.askstring("Edit Category", "Enter new category:", initialvalue=selected_expense[2])
            new_currency = simpledialog.askstring("Edit Currency", "Enter new currency:", initialvalue=selected_expense[3])
            new_date = simpledialog.askstring("Edit Date", "Enter new date (YYYY-MM-DD):", initialvalue=selected_expense[4])

            if new_expense and new_item and new_category and new_currency and new_date:
                self.expenses[selected_index] = (new_expense, new_item, new_category, new_currency, new_date)
                self.refresh_list()
                self.update_total_label()

    def delete_expense(self):
        selected_index = self.expense_listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]
            del self.expenses[selected_index]
            self.expense_listbox.delete(selected_index)
            self.update_total_label()

    def refresh_list(self):
        self.expense_listbox.delete(0, tk.END)
        for expense in self.expenses:
            self.expense_listbox.insert(tk.END, f"{expense[0]} - {expense[1]} - {expense[2]} - {expense[3]} ({expense[4]})")

    def update_total_label(self):
        total_expenses = sum(float(expense[0]) for expense in self.expenses)
        self.total_label.config(text=f"Total Expenses:  {total_expenses:.2f}")

    def save_expenses(self):
        with open("expenses.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            column_headers = ["Expense Amount", "Item Description", "Category", "Currency", "Date"]
            writer.writerow(column_headers)
            for expense in self.expenses:
                writer.writerow(expense)

    def load_expenses(self):
        try:
            with open("expenses.csv", "r") as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip the header
                for row in reader:
                    if len(row) == 5:  # Expense, item, category, currency, date
                        self.expenses.append(tuple(row))
                self.refresh_list()
        except FileNotFoundError:
            pass

    def show_expenses_chart(self):
        category_totals = {}
        for expense, _, category, _, _ in self.expenses:
            try:
                amount = float(expense)
            except ValueError:
                continue
            category_totals[category] = category_totals.get(category, 0) + amount

        categories = list(category_totals.keys())
        expenses = list(category_totals.values())
        plt.figure(figsize=(8, 6))
        plt.pie(expenses, labels=categories, autopct="%1.1f%%", startangle=140, shadow=True)
        plt.axis("equal")
        plt.title("Expense Categories Distribution")
        plt.show()

    def extract_text_from_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Receipt Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.gif")]
        )

        if file_path:
            try:
                img = Image.open(file_path)
                extracted_text = pytesseract.image_to_string(img)
                if extracted_text:
                    messagebox.showinfo("OCR Output", f"Extracted Text:\n{extracted_text}")
                    self.parse_ocr_text(extracted_text)
                else:
                    messagebox.showwarning("OCR Error", "No text was extracted from the image.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process image. Error: {e}")

    def parse_ocr_text(self, ocr_text):
        amount_match = re.search(r'(\d+\.\d{2})', ocr_text)
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', ocr_text)

        if amount_match and date_match:
            amount = amount_match.group(0)
            date = date_match.group(0)
            self.expenses.append((amount, "Extracted Item", "Other", "USD", date))
            self.refresh_list()
            self.update_total_label()
            messagebox.showinfo("Success", "Expense extracted and added.")
        else:
            messagebox.showwarning("Parsing Error", "Could not find amount or date in the OCR text.")


if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.mainloop()
