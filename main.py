import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
from datetime import datetime

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.expenses = []
        self.filepath = "expenses.json"

        self.create_widgets()
        self.load_expenses()

    def create_widgets(self):
        # --- Форма добавления расхода ---
        form_frame = ttk.LabelFrame(self.root, text="Добавить расход")
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(form_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(form_frame)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Категория:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.category_entry = ttk.Entry(form_frame)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Дата (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = ttk.Entry(form_frame)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) # Предзаполнение текущей датой
        self.date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        add_button = ttk.Button(form_frame, text="Добавить расход", command=self.add_expense)
        add_button.grid(row=3, column=0, columnspan=2, pady=10)

        # --- Таблица расходов ---
        table_frame = ttk.LabelFrame(self.root, text="Расходы")
        table_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky="nsew")

        self.tree = ttk.Treeview(table_frame, columns=("Сумма", "Категория", "Дата"), show="headings")
        self.tree.heading("Сумма", text="Сумма")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # --- Фильтрация ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтр")
        filter_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category_entry = ttk.Entry(filter_frame)
        self.filter_category_entry.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Дата от (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.filter_date_start_entry = ttk.Entry(filter_frame)
        self.filter_date_start_entry.grid(row=1, column=1, padx=5)

        ttk.Label(filter_frame, text="Дата до (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
        self.filter_date_end_entry = ttk.Entry(filter_frame)
        self.filter_date_end_entry.grid(row=2, column=1, padx=5)

        filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_button.grid(row=3, column=0, columnspan=2, pady=5)

        clear_filter_button = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.clear_filter)
        clear_filter_button.grid(row=4, column=0, columnspan=2, pady=5)

        # --- Подсчет суммы ---
        summary_frame = ttk.Frame(self.root)
        summary_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.summary_label = ttk.Label(summary_frame, text="Общая сумма за период: 0")
        self.summary_label.pack()

        # --- Кнопки сохранения/загрузки ---
        save_load_frame = ttk.Frame(self.root)
        save_load_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        save_button = ttk.Button(save_load_frame, text="Сохранить", command=self.save_expenses)
        save_button.grid(row=0, column=0, padx=5)

        load_button = ttk.Button(save_load_frame, text="Загрузить", command=self.load_expenses)
        load_button.grid(row=0, column=1, padx=5)

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def is_valid_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_expense(self):
        amount_str = self.amount_entry.get()
        category = self.category_entry.get()
        date_str = self.date_entry.get()

        if not amount_str or not category or not date_str:
            messagebox.showwarning("Ошибка ввода", "Все поля должны быть заполнены.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("Ошибка ввода", "Сумма должна быть положительным числом.")
                return
        except ValueError:
            messagebox.showwarning("Ошибка ввода", "Сумма должна быть числом.")
            return

        if not self.is_valid_date(date_str):
            messagebox.showwarning("Ошибка ввода", "Дата должна быть в формате YYYY-MM-DD.")
            return

        self.expenses.append({"amount": amount, "category": category, "date": date_str})
        self.update_table()
        date_str = datetime.now().strftime("%Y-%m-%d") # Сброс даты на текущую после добавления
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date_str)
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)

    def update_table(self, filtered_expenses=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        expenses_to_display = filtered_expenses if filtered_expenses is not None else self.expenses

        for expense in expenses_to_display:
            self.tree.insert("", tk.END, values=(expense["amount"], expense["category"], expense["date"]))
        self.calculate_summary(expenses_to_display)

    def calculate_summary(self, expenses_list):
        total_amount = sum(expense["amount"] for expense in expenses_list)
        self.summary_label.config(text=f"Общая сумма за период: {total_amount:.2f}")

    def apply_filter(self):
        filter_category = self.filter_category_entry.get().lower()
        filter_date_start_str = self.filter_date_start_entry.get()
        filter_date_end_str = self.filter_date_end_entry.get()

        filtered_expenses = []
        for expense in self.expenses:
            match_category = True
            if filter_category and filter_category not in expense["category"].lower():
                match_category = False

            match_date = True
            try:
                expense_date = datetime.strptime(expense["date"], "%Y-%m-%d")
                if filter_date_start_str:
                    start_date = datetime.strptime(filter_date_start_str, "%Y-%m-%d")
                    if expense_date < start_date:
                        match_date = False
                if filter_date_end_str:
                    end_date = datetime.strptime(filter_date_end_str, "%Y-%m-%d")
                    if expense_date > end_date:
                        match_date = False
            except ValueError:
                # Если дата в расходе некорректна, пропускаем ее для фильтрации
                match_date = False


            if match_category and match_date:
                filtered_expenses.append(expense)

        self.update_table(filtered_expenses)

    def clear_filter(self):
        self.filter_category_entry.delete(0, tk.END)
        self.filter_date_start_entry.delete(0, tk.END)
        self.filter_date_end_entry.delete(0, tk.END)
        self.update_table()

    def save_expenses(self):
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.expenses, f, indent=4)
            messagebox.showinfo("Сохранение", "Данные успешно сохранены.")
        except IOError:
            messagebox.showerror("Ошибка сохранения", "Не удалось сохранить данные.")

    def load_expenses(self):
        try:
            with open(self.filepath, 'r') as f:
                self.expenses = json.load(f)
            self.update_table()
            messagebox.showinfo("Загрузка", "Данные успешно загружены.")
        except FileNotFoundError:
            self.expenses = [] # Если файл не найден, начинаем с пустого списка
            messagebox.showinfo("Загрузка", "Файл с данными не найден. Создан новый список расходов.")
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка загрузки", "Не удалось прочитать файл JSON. Файл может быть поврежден.")
            self.expenses = [] # В случае ошибки декодирования, очищаем список
        except IOError:
            messagebox.showerror("Ошибка загрузки", "Не удалось загрузить данные.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
