import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from rabin import RabinServer, encrypt_file, decrypt_file

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class RabinApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Криптосистема Рабина")
        self.geometry("800x700")
        self.minsize(600, 600)
        
        self.server = RabinServer(key_size=512)
        self.current_file = None
        
        self.create_widgets()
        self.update_key_display()
    
    def create_widgets(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.key_tab = self.tabview.add("Ключи")
        self.file_tab = self.tabview.add("Файлы")
        self.about_tab = self.tabview.add("О программе")
        
        self.setup_key_tab()
        self.setup_file_tab()
        self.setup_about_tab()
    
    def setup_key_tab(self):
        key_gen_frame = ctk.CTkFrame(self.key_tab)
        key_gen_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(key_gen_frame, text="Генерация ключей:", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        ctk.CTkButton(key_gen_frame, text="Сгенерировать новые ключи", 
                     command=self.generate_keys, height=40).pack(padx=10, pady=10)
        
        key_size_frame = ctk.CTkFrame(self.key_tab)
        key_size_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(key_size_frame, text="Размер ключа (бит):", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 2))
        
        self.key_size_var = ctk.StringVar(value="512")
        key_size_combo = ctk.CTkComboBox(key_size_frame, values=["256", "512", "1024"], 
                                       variable=self.key_size_var, width=150)
        key_size_combo.pack(anchor="w", padx=10, pady=5)
        
        key_display_frame = ctk.CTkFrame(self.key_tab)
        key_display_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(key_display_frame, text="Публичный ключ (n):", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.public_key_display = ctk.CTkTextbox(key_display_frame, height=80, font=("Consolas", 10))
        self.public_key_display.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(key_display_frame, text="Приватные ключи (p, q, yp, yq):", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.private_key_display = ctk.CTkTextbox(key_display_frame, height=120, font=("Consolas", 10))
        self.private_key_display.pack(fill="both", expand=True, padx=10, pady=5)
    
    def setup_file_tab(self):
        file_frame = ctk.CTkFrame(self.file_tab)
        file_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(file_frame, text="Работа с файлами:", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.file_label = ctk.CTkLabel(file_frame, text="Файл не выбран", font=("Arial", 12))
        self.file_label.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(file_frame, text="Выбрать файл", command=self.select_file).pack(padx=10, pady=5)
        
        file_buttons_frame = ctk.CTkFrame(self.file_tab)
        file_buttons_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(file_buttons_frame, text="Зашифровать файл", command=self.encrypt_file_gui).pack(side="left", padx=5)
        ctk.CTkButton(file_buttons_frame, text="Расшифровать файл", command=self.decrypt_file_gui).pack(side="left", padx=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.file_tab)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self.file_tab, text="Готов", font=("Arial", 12))
        self.status_label.pack(fill="x", padx=10, pady=5)
    
    def setup_about_tab(self):
        about_text = """
  
        Алгоритм:
        1. Генерация ключей: выбираются два больших простых числа p и q
        2. Публичный ключ: n = p × q
        3. Шифрование: c = m² mod n
        4. Дешифрование: нахождение квадратных корней по модулям p и q
           с последующей комбинацией по китайской теореме об остатках
        
        Примечание: При дешифровании получается 4 возможных решения,
        одно из которых является исходным сообщением.
        
        Расшифрование основано на сложности криптосистемы — извлечение квадратного корня по модулю. С помощью расширенного алгоритма Евклида находятся 
        коэффициенты для решения уравнения. Это необходимо для применения китайской теоремы об остатках. Вычисляются квадратные корни по модулю чисел p и q. 
        Поскольку квадратный корень может иметь два значения, для каждого из них получаем два корня. С помощью китайской теоремы корни объединяются 
        для получения окончательного результата.
        
        Реализация соответствует лабораторной работе №3
        по асимметричной криптографии.
        """
        text_widget = ctk.CTkTextbox(self.about_tab, wrap="word", font=("Arial", 12))
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        text_widget.insert("1.0", about_text)
        text_widget.configure(state="disabled")
    
    def generate_keys(self):
        try:
            key_size = int(self.key_size_var.get())
            self.server = RabinServer(key_size=key_size)
            public_key = self.server.generate_keys()
            
            if public_key:
                self.update_key_display()
                messagebox.showinfo("Успех", f"Ключи сгенерированы!\nРазмер ключа: {public_key.bit_length()} бит")
            else:
                messagebox.showerror("Ошибка", "Не удалось сгенерировать ключи")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при генерации ключей: {str(e)}")
    
    def update_key_display(self):
        public_key = self.server.get_public_key()
        if public_key:
            self.public_key_display.delete("1.0", "end")
            self.public_key_display.insert("1.0", f"n = {public_key}\n\nБит: {public_key.bit_length()}")
        
        private_key = self.server.get_private_key()
        if private_key:
            self.private_key_display.delete("1.0", "end")
            p, q, yp, yq = private_key
            self.private_key_display.insert("1.0", f"p = {p}\n\nq = {q}\n\ny_p = {yp}\n\ny_q = {yq}")
    
    def select_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.current_file = filename
            self.file_label.configure(text=f"Выбран файл: {os.path.basename(filename)}")
    
    def encrypt_file_gui(self):
        if not self.current_file or not self.server.get_public_key():
            return
        output_file = filedialog.asksaveasfilename(defaultextension=".rabin")
        if output_file:
            threading.Thread(target=encrypt_file, args=(self.current_file, output_file, self.server)).start()
    
    def decrypt_file_gui(self):
        if not self.current_file or not self.server.get_private_key():
            return
        output_file = filedialog.asksaveasfilename(defaultextension=".txt")
        if output_file:
            threading.Thread(target=decrypt_file, args=(self.current_file, output_file, self.server)).start()

if __name__ == "__main__":
    app = RabinApp()
    app.mainloop()
