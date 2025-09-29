import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from gost import GOST28147_89

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue") 


class GOSTApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("GOST 28147-89 Encryption Tool")
        self.geometry("600x600")
        self.minsize(400, 400)
        
        self.key = os.urandom(32)
        self.current_file = None
        
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
    
    def setup_file_tab(self):
        file_frame = ctk.CTkFrame(self.file_tab)
        file_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(file_frame, text="Работа с файлами:", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.file_label = ctk.CTkLabel(file_frame, text="Файл не выбран", font=("Arial", 12))
        self.file_label.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(file_frame, text="Выбрать файл", command=self.select_file).pack(padx=10, pady=5)
        
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
            GOST 28147-89 Encryption Tool
            
            Программа для шифрования и дешифрования данных 
            с использованием алгоритма ГОСТ 28147-89.
            
            Особенности:
            - 256-битное шифрование
            - Режим ECB (Простой замены)
            - Поддержка текста и файлов
            - Современный графический интерфейс
            
            Алгоритм ГОСТ 28147-89 является стандартом 
            симметричного шифрования в России.
            
        """
        
        text_widget = ctk.CTkTextbox(self.about_tab, wrap="word", font=("Arial", 12))
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        text_widget.insert("1.0", about_text)
        text_widget.configure(state="disabled")
    
    def generate_new_key(self):
        self.key = os.urandom(32)
        self.update_key_display()
        messagebox.showinfo("Успех", "Новый ключ сгенерирован!")
    
    def update_key_display(self):
        self.key_display.configure(text=self.key.hex())
    
    def encrypt_text(self):
        try:
            text = self.input_text.get("1.0", "end-1c").encode('utf-8')
            if not text:
                messagebox.showwarning("Предупреждение", "Введите текст для шифрования")
                return
            
            gost = GOST28147_89(self.key)
            encrypted = gost.encrypt_ecb(text)
            
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
            gost = GOST28147_89(self.key)
            decrypted = gost.decrypt_ecb(encrypted_data)
            
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
            threading.Thread(target=self._encrypt_file_thread, args=(self.current_file, output_file)).start()
    
    def decrypt_file(self):
        if not self.current_file:
            messagebox.showwarning("Предупреждение", "Сначала выберите файл")
            return
        
        output_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("All files", "*.*")]
        )
        
        if output_file:
            threading.Thread(target=self._decrypt_file_thread, args=(self.current_file, output_file)).start()
    
    def _encrypt_file_thread(self, input_file, output_file):
        try:
            self.progress_bar.set(0)
            self.status_label.configure(text="Шифрование...")
            
            gost = GOST28147_89(self.key)
            
            with open(input_file, 'rb') as f:
                plaintext = f.read()
            
            ciphertext = gost.encrypt_ecb(plaintext)
            
            with open(output_file, 'wb') as f:
                f.write(ciphertext)
            
            self.progress_bar.set(1.0)
            self.status_label.configure(text="Шифрование завершено!")
            messagebox.showinfo("Успех", f"Файл успешно зашифрован!\nСохранен как: {output_file}")
            
        except Exception as e:
            self.status_label.configure(text="Ошибка!")
            messagebox.showerror("Ошибка", f"Ошибка при шифровании файла: {str(e)}")
    
    def _decrypt_file_thread(self, input_file, output_file):
        try:
            self.progress_bar.set(0)
            self.status_label.configure(text="Дешифрование...")
            
            gost = GOST28147_89(self.key)
            
            with open(input_file, 'rb') as f:
                ciphertext = f.read()
            
            plaintext = gost.decrypt_ecb(ciphertext)
            
            with open(output_file, 'wb') as f:
                f.write(plaintext)
            
            self.progress_bar.set(1.0)
            self.status_label.configure(text="Дешифрование завершено!")
            messagebox.showinfo("Успех", f"Файл успешно дешифрован!\nСохранен как: {output_file}")
            
        except Exception as e:
            self.status_label.configure(text="Ошибка!")
            messagebox.showerror("Ошибка", f"Ошибка при дешифровании файла: {str(e)}")


if __name__ == "__main__":
    app = GOSTApp()
    app.mainloop()
