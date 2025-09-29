import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from belt import belt_simple_replace, belt_feedback_gamma

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue") 


class BELTApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("BELST Encryption Tool")
        self.geometry("700x700")
        self.minsize(500, 500)
        
        self.key = os.urandom(32)
        print(self.key)
        self.current_file = None
        self.mode_var = ctk.StringVar(value="simple")
        self.s_var = os.urandom(16)
        
        self.create_widgets()
        self.update_key_display()
    
    def create_widgets(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.text_tab = self.tabview.add("Текст")
        self.file_tab = self.tabview.add("Файлы")
        self.about_tab = self.tabview.add("О программе")
        
        self.setup_text_tab()
        self.setup_file_tab()
        self.setup_about_tab()
    
    def setup_text_tab(self):
        key_frame = ctk.CTkFrame(self.text_tab)
        key_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(key_frame, text="256-битный ключ:", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.key_display = ctk.CTkLabel(key_frame, text="", font=("Consolas", 12))
        self.key_display.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(key_frame, text="Сгенерировать новый ключ", command=self.generate_new_key).pack(padx=10, pady=5)
        
        mode_frame = ctk.CTkFrame(self.text_tab)
        mode_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(mode_frame, text="Режим шифрования:", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        ctk.CTkRadioButton(mode_frame, text="Простая замена", variable=self.mode_var, value="simple").pack(anchor="w", padx=20)
        ctk.CTkRadioButton(mode_frame, text="Гаммирование с обратной связью", variable=self.mode_var, value="feedback").pack(anchor="w", padx=20)
        
        self.s_frame = ctk.CTkFrame(self.text_tab)
        self.s_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(self.s_frame, text="S-параметр (16 байт):", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 2))
        
        self.s_display = ctk.CTkLabel(self.s_frame, text="", font=("Consolas", 10))
        self.s_display.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkButton(self.s_frame, text="Сгенерировать новый S", command=self.generate_new_s, width=200).pack(padx=10, pady=5)
        
        text_frame = ctk.CTkFrame(self.text_tab)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(text_frame, text="Исходный текст:", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.input_text = ctk.CTkTextbox(text_frame, height=100)
        self.input_text.pack(fill="x", padx=10, pady=5)
        
        button_frame = ctk.CTkFrame(text_frame)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(button_frame, text="Зашифровать", command=self.encrypt_text).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Расшифровать", command=self.decrypt_text).pack(side="left", padx=5)
        
        ctk.CTkLabel(text_frame, text="Результат:", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.result_text = ctk.CTkTextbox(text_frame, height=100)
        self.result_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.mode_var.trace('w', self.update_s_visibility)
        self.update_s_visibility()
    
    def setup_file_tab(self):
        file_frame = ctk.CTkFrame(self.file_tab)
        file_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(file_frame, text="Работа с файлами:", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.file_label = ctk.CTkLabel(file_frame, text="Файл не выбран", font=("Arial", 12))
        self.file_label.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(file_frame, text="Выбрать файл", command=self.select_file).pack(padx=10, pady=5)
        
        file_mode_frame = ctk.CTkFrame(self.file_tab)
        file_mode_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(file_mode_frame, text="Режим шифрования:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 2))
        
        self.file_mode_var = ctk.StringVar(value="simple")
        ctk.CTkRadioButton(file_mode_frame, text="Простая замена", variable=self.file_mode_var, value="simple").pack(anchor="w", padx=20)
        ctk.CTkRadioButton(file_mode_frame, text="Гаммирование с обратной связью", variable=self.file_mode_var, value="feedback").pack(anchor="w", padx=20)
        
        button_frame = ctk.CTkFrame(self.file_tab)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(button_frame, text="Зашифровать файл", command=self.encrypt_file).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(button_frame, text="Расшифровать файл", command=self.decrypt_file).pack(side="left", padx=5, pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.file_tab)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self.file_tab, text="Готов", font=("Arial", 12))
        self.status_label.pack(fill="x", padx=10, pady=5)
    
    def setup_about_tab(self):
        about_text = """
            BELST Encryption Tool
            
            Программа для шифрования и дешифрования данных 
            с использованием алгоритма BELT (белорусский стандарт).
            
            Особенности:
            - 256-битное шифрование
            - Два режима работы:
              * Простая замена
              * Гаммирование с обратной связью
            - Поддержка текста и файлов
            - Современный графический интерфейс
            
            Алгоритм BELT является стандартом симметричного 
            шифрования в Беларуси.
            
            Алгоритм шифрования в режиме простой замены: сообщение разбивается на блоки по 128 бит (16 байт). Каждый блок шифруется последовательно, 
            используя 256 бит (32 байта). Преобразования внутри блока включают суммирование чисел, циклический сдвиг влево и подстановку по фиксированной 
            таблице. Блок разбивается на 4 части, для каждого блока вводится такт, выполняется 32-битное сложение функции с текущим значением блока, 
            циклический сдвиг влево на 1 бит и подстановка по таблице. Для расшифровывания блока необходимо использовать блоки в обратном порядке, 
            алгоритм расшифровки аналогичен шифрованию, но текст нельзя получить без ключа.
            
        """
        
        text_widget = ctk.CTkTextbox(self.about_tab, wrap="word", font=("Arial", 12))
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        text_widget.insert("1.0", about_text)
        text_widget.configure(state="disabled")
    
    def generate_new_key(self):
        self.key = os.urandom(32)
        self.update_key_display()
        messagebox.showinfo("Успех", "Новый ключ сгенерирован!")
    
    def generate_new_s(self):
        self.s_var = os.urandom(16)
        self.update_s_display()
        messagebox.showinfo("Успех", "Новый S-параметр сгенерирован!")
    
    def update_key_display(self):
        self.key_display.configure(text=self.key.hex())
    
    def update_s_display(self):
        self.s_display.configure(text=self.s_var.hex())
    
    def update_s_visibility(self, *args):
        if self.mode_var.get() == "feedback":
            self.s_frame.pack(fill="x", padx=10, pady=5)
            self.update_s_display()
        else:
            self.s_frame.pack_forget()
    
    def encrypt_text(self):
        try:
            text = self.input_text.get("1.0", "end-1c").encode('utf-8')
            if not text:
                messagebox.showwarning("Предупреждение", "Введите текст для шифрования")
                return
            
            mode = self.mode_var.get()
            if mode == "simple":
                encrypted = belt_simple_replace(text, self.key, 'encrypt')
            else:
                encrypted = belt_feedback_gamma(text, self.key, self.s_var, 'encrypt')
            
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", encrypted.hex())
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при шифровании: {str(e)}")
    
    def decrypt_text(self):
        try:
            hex_text = self.result_text.get("1.0", "end-1c").strip()
            if not hex_text:
                messagebox.showwarning("Предупреждение", "Введите hex-текст для дешифрования")
                return
            
            encrypted_data = bytes.fromhex(hex_text)
            mode = self.mode_var.get()
            
            if mode == "simple":
                decrypted = belt_simple_replace(encrypted_data, self.key, 'decrypt')
            else:
                decrypted = belt_feedback_gamma(encrypted_data, self.key, self.s_var, 'decrypt')
            
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", decrypted.decode('utf-8', errors='ignore'))
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при дешифровании: {str(e)}")
    
    def select_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.current_file = filename
            self.file_label.configure(text=f"Выбран файл: {os.path.basename(filename)}")
    
    def encrypt_file(self):
        if not self.current_file:
            messagebox.showwarning("Предупреждение", "Сначала выберите файл")
            return
        
        output_file = filedialog.asksaveasfilename(
            defaultextension=".enc",
            filetypes=[("Encrypted files", "*.enc"), ("All files", "*.*")]
        )
        
        if output_file:
            mode = self.file_mode_var.get()
            threading.Thread(target=self._encrypt_file_thread, args=(self.current_file, output_file, mode)).start()
    
    def decrypt_file(self):
        if not self.current_file:
            messagebox.showwarning("Предупреждение", "Сначала выберите файл")
            return
        
        output_file = filedialog.asksaveasfilename(
            defaultextension=".dec",
            filetypes=[("All files", "*.*")]
        )
        
        if output_file:
            mode = self.file_mode_var.get()
            threading.Thread(target=self._decrypt_file_thread, args=(self.current_file, output_file, mode)).start()
    
    def _encrypt_file_thread(self, input_file, output_file, mode):
        try:
            self.progress_bar.set(0)
            self.status_label.configure(text="Шифрование...")
            
            with open(input_file, 'rb') as f:
                plaintext = f.read()
            
            if mode == "simple":
                ciphertext = belt_simple_replace(plaintext, self.key, 'encrypt')
            else:
                ciphertext = belt_feedback_gamma(plaintext, self.key, self.s_var, 'encrypt')
            
            with open(output_file, 'wb') as f:
                f.write(ciphertext)
            
            self.progress_bar.set(1.0)
            self.status_label.configure(text="Шифрование завершено!")
            messagebox.showinfo("Успех", f"Файл успешно зашифрован!\nСохранен как: {output_file}")
            
        except Exception as e:
            self.status_label.configure(text="Ошибка!")
            messagebox.showerror("Ошибка", f"Ошибка при шифровании файла: {str(e)}")
    
    def _decrypt_file_thread(self, input_file, output_file, mode):
        try:
            self.progress_bar.set(0)
            self.status_label.configure(text="Дешифрование...")
            
            with open(input_file, 'rb') as f:
                ciphertext = f.read()
            
            if mode == "simple":
                plaintext = belt_simple_replace(ciphertext, self.key, 'decrypt')
            else:
                plaintext = belt_feedback_gamma(ciphertext, self.key, self.s_var, 'decrypt')
            
            plaintext = plaintext.rstrip((b'\x00'))
            
            with open(output_file, 'wb') as f:
                
                f.write(plaintext)
            
            self.progress_bar.set(1.0)
            self.status_label.configure(text="Дешифрование завершено!")
            messagebox.showinfo("Успех", f"Файл успешно дешифрован!\nСохранен как: {output_file}")
            
        except Exception as e:
            self.status_label.configure(text="Ошибка!")
            messagebox.showerror("Ошибка", f"Ошибка при дешифровании файла: {str(e)}")


if __name__ == "__main__":
    app = BELTApp()
    app.mainloop()