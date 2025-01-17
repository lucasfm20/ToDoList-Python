import customtkinter as ctk
import tkinter as tk
import sqlite3
import banco
import automacao

class ToDoListApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List")
        self.geometry("400x500")
        ctk.set_appearance_mode("dark")
        
        self.conn = sqlite3.connect('meu_banco_de_dados.db')
        self.cursor = self.conn.cursor()

        # self.cursor.execute('DROP TABLE IF EXISTS tarefas')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL
        )
        ''')
        self.conn.commit()

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS email (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL
        )
        ''')
        self.conn.commit()

        # Lista de tarefas
        self.tasks = []

        # Frame principal
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(padx=20, pady=20, fill='both', expand=True)

        # Entrada para novas tarefas
        self.entry = ctk.CTkEntry(self.frame, placeholder_text="Adicione uma nova tarefa")
        self.entry.pack(pady=(0, 10), fill='x')
        self.entry.bind('<Return>', self.on_enter_key)  # Bind da tecla Enter

        # Botão para adicionar tarefas
        self.add_button = ctk.CTkButton(self.frame, text="Adicionar", command=self.add_task)
        self.add_button.pack(pady=(0, 20))

        # Frame para as tarefas
        self.tasks_frame = ctk.CTkFrame(self.frame)
        self.tasks_frame.pack(fill='both', expand=True)

        # Botão para remover tarefas selecionadas
        self.remove_button = ctk.CTkButton(self.frame, text="Remover selecionadas", command=self.remove_tasks)
        self.remove_button.pack(pady=(10, 0))

        self.envia = ctk.CTkButton(self.frame, text="Enviar por email", command=self.envia_mail)
        self.envia.pack(pady=(10, 0))


        
        # Carregar tarefas do banco de dados
        self.load_tasks()

    def on_enter_key(self, event):
        self.add_task()

    def load_tasks(self):
        self.cursor.execute('SELECT * FROM tarefas')
        tarefas = self.cursor.fetchall()
        for tarefa in tarefas:
            task_var = tk.BooleanVar(value=False)
            task_check = ctk.CTkCheckBox(self.tasks_frame, text=tarefa[1], variable=task_var)
            task_check.pack(anchor='w', pady=5)
            self.tasks.append((task_check, task_var))

    def add_task(self):
        task_text = self.entry.get()
        if task_text:
            task_var = tk.BooleanVar()
            task_check = ctk.CTkCheckBox(self.tasks_frame, text=task_text, variable=task_var, corner_radius=5, height=5)
            task_check.pack(anchor='w', pady=5)
            self.tasks.append((task_check, task_var))
            self.entry.delete(0, tk.END)

            # Inserir a nova tarefa no banco de dados 
            self.cursor.execute('''
            INSERT INTO tarefas (descricao)
            VALUES (?)
            ''', (task_text,))
            self.conn.commit()

    def remove_tasks(self):
        for task_check, task_var in self.tasks[:]:
            if task_var.get():
                # Remover do banco de dados
                self.cursor.execute('''
                DELETE FROM tarefas
                WHERE descricao = ?
                ''', (task_check.cget('text'),))
                self.conn.commit()
                
                task_check.destroy()
                self.tasks.remove((task_check, task_var))

    def envia_mail(self):
        email_window = ctk.CTkToplevel(self)
        email_window.title("Enviar Email")
        email_window.geometry("300x200")

        email_label = ctk.CTkLabel(email_window, text="Digite o email:")
        email_label.pack(pady=10)
        

        email_entry = ctk.CTkEntry(email_window)
        email_entry.pack(pady=10, fill='x', padx=20)

        send_button = ctk.CTkButton(email_window, text="Enviar", command=lambda: self.send_email(email_entry.get(), email_window))
        send_button.pack(pady=10)

        

    def send_email(self, email, email_window):
        self.cursor.execute('''
            INSERT INTO email (descricao)
            VALUES (?)
            ''', (email,))
        self.conn.commit()

        tasks = banco.listaTarefas()
        if tasks:
            automacao.geraEmail(tasks, email)
            
        email_window.destroy()
        
        
       

if __name__ == "__main__":
    app = ToDoListApp()
    app.mainloop()
