import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tk_messagebox
from PIL import Image, ImageTk
import mysql.connector

class FinanceTracker(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Учет личных финансов")
        self.geometry("800x500")

        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="mydb"
        )
        self.c = self.conn.cursor()

        self.child_window = None

        self.create_main_window()

    def create_main_window(self):
        self.tree = ttk.Treeview(self, columns=("description", "category", "amount"))
        self.tree.heading("#0", text="ID")
        self.tree.heading("description", text="Наименование")
        self.tree.heading("category", text="Статья дохода/расхода")
        self.tree.heading("amount", text="Сумма")
        self.tree.pack(fill="both", expand=True)

        frame_buttons = tk.Frame(self)
        frame_buttons.pack(pady=10)

        self.btn_add = self.create_button("add.png", "Добавить", frame_buttons, 0, 0, self.show_child_window)
        self.btn_edit = self.create_button("update.png", "Редактировать", frame_buttons, 0, 1, self.edit_record)
        self.btn_delete = self.create_button("delete.png", "Удалить", frame_buttons, 0, 2, self.delete_record)
        self.btn_search = self.create_button("search.png", "Поиск", frame_buttons, 0, 3, self.show_search_window)
        self.btn_refresh = self.create_button("refresh.png", "Обновить", frame_buttons, 0, 4, self.view_records)

        self.view_records()

    def create_button(self, image_name, text, parent, row, column, command):
        image = Image.open(image_name)
        image = image.resize((30, 30), resample=Image.BICUBIC)
        photo = ImageTk.PhotoImage(image)
        button = ttk.Button(parent, image=photo, text=text, compound="top", command=command)
        button.image = photo
        button.grid(row=row, column=column, padx=10)
        return button

    def show_child_window(self):
        if not self.child_window or not self.child_window.winfo_exists():
            self.child_window = ChildWindow(self)

    def edit_record(self):
        if self.tree.selection():
            self.child_window = UpdateChild(self)

    def delete_record(self):
        selected = self.tree.selection()
        if selected:
            if tk_messagebox.askyesno("Удаление", "Вы уверены, что хотите удалить эту запись?"):
                self.c.execute("DELETE FROM transactions WHERE id = %s", (int(selected[0]),))
                self.conn.commit()
                self.tree.delete(selected[0])

    def show_search_window(self):
        self.child_window = SearchWindow(self)

    def view_records(self):
        self.c.execute("SELECT * FROM transactions")
        records = self.c.fetchall()
        self.tree.delete(*self.tree.get_children())
        for record in records:
            self.tree.insert("", "end", str(record[0]), text=str(record[0]), values=(record[1], record[2], record[3]))

    def add_record(self, description, category, amount):
        self.c.execute("INSERT INTO transactions (description, category, amount) VALUES (%s, %s, %s)", (description, category, amount))
        self.conn.commit()
        self.view_records()

    def edit_existing_record(self, index, description, amount):
        self.c.execute("UPDATE transactions SET description = %s, amount = %s WHERE id = %s", (description, amount, index))
        self.conn.commit()
        self.view_records()

    def search_records(self, query):

        self.c.execute("SELECT * FROM transactions WHERE description LIKE %s", (f"%{query}%",))
        records = self.c.fetchall()
        return records

    def del_db(self):
        self.conn.close()

class ChildWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Новая транзакция")
        self.geometry("400x200")

        self.description = tk.StringVar()
        self.category = tk.StringVar()
        self.amount = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Наименование:").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(self, textvariable=self.description).grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self, text="Статья дохода/расхода:").grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(self, textvariable=self.category).grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self, text="Сумма:").grid(row=2, column=0, padx=10, pady=10)
        tk.Entry(self, textvariable=self.amount).grid(row=2, column=1, padx=10, pady=10)

        tk.Button(self, text="Сохранить", command=self.save_record).grid(row=3, column=0, padx=10, pady=10)
        tk.Button(self, text="Отмена", command=self.destroy).grid(row=3, column=1, padx=10, pady=10)

    def save_record(self):
        description = self.description.get()
        category = self.category.get()
        amount = float(self.amount.get())
        self.master.add_record(description, category, amount)
        self.destroy()

class UpdateChild(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Редактировать транзакцию")
        self.geometry("400x200")

        self.selected_id = self.master.tree.selection()[0]
        self.description = tk.StringVar()
        self.amount = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        self.c.execute("SELECT description, amount FROM transactions WHERE id = %s", (self.selected_id,))
        result = self.c.fetchone()

        self.description.set(result[0])
        self.amount.set(result[1])

        tk.Label(self, text="Наименование:").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(self, textvariable=self.description).grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self, text="Сумма:").grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(self, textvariable=self.amount).grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self, text="Сохранить", command=self.update_record).grid(row=2, column=0, padx=10, pady=10)
        tk.Button(self, text="Отмена", command=self.destroy).grid(row=2, column=1, padx=10, pady=10)

    def update_record(self):
        description = self.description.get()
        amount = float(self.amount.get())
        self.master.edit_existing_record(self.selected_id, description, amount)
        self.destroy()

class SearchWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Поиск")
        self.geometry("400x200")

        self.search_query = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Поиск:").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(self, textvariable=self.search_query).grid(row=0, column=1, padx=10, pady=10)

        tk.Button(self, text="Найти", command=self.search_records).grid(row=1, column=0, padx=10, pady=10)
        tk.Button(self, text="Отмена", command=self.destroy).grid(row=1, column=1, padx=10, pady=10)

        self.result_tree = ttk.Treeview(self, columns=("description", "category", "amount"))

        self.result_tree.heading("#0", text="ID")
        self.result_tree.heading("description", text="Наименование")
        self.result_tree.heading("category", text="Статья дохода/расхода")
        self.result_tree.heading("amount", text="Сумма")
        self.result_tree.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    def search_records(self):
        query = self.search_query.get()
        records = self.master.search_records(query)
        self.result_tree.delete(*self.result_tree.get_children())
        for record in records:
            self.result_tree.insert("", "end", str(record[0]), text=str(record[0]), values=(record[1], record[2], record[3]))

if __name__ == "__main__":
    app = FinanceTracker(None)
    app.mainloop()
