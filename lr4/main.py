import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import numpy as np
import random
from mc_eliece import *

class McElieceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Криптосистема Мак-Элиса")
        self.geometry("900x750")
        self.minsize(700, 650)
        
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
        
        key_info_frame = ctk.CTkFrame(self.key_tab)
        key_info_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(key_info_frame, text="Параметры системы:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 2))
        ctk.CTkLabel(key_info_frame, text="Код Хэмминга (7,4)", font=("Arial", 10)).pack(anchor="w", padx=10, pady=2)
        
        key_display_frame = ctk.CTkFrame(self.key_tab)
        key_display_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(key_display_frame, text="Публичный ключ (G_hat):", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.public_key_display = ctk.CTkTextbox(key_display_frame, height=100, font=("Consolas", 10))
        self.public_key_display.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(key_display_frame, text="Приватные ключи (S, P):", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.private_key_display = ctk.CTkTextbox(key_display_frame, height=150, font=("Consolas", 10))
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
Криптосистема Мак-Элиса
        
Особенности:
- Безопасность основана на сложности декодирования общих линейных кодов
        
Алгоритм:
1. Генерация ключей: 
   - S: случайная невырожденная матрица 4×4
   - P: случайная перестановочная матрица 7×7
   - G_hat = S × G^T × P (публичный ключ)
        
2. Шифрование: 
   - Сообщение разбивается на блоки по 4 бита
   - Каждый блок кодируется с помощью G_hat
   - Добавляется случайная ошибка (1 бит)
        
3. Дешифрование:
   - Применяется P^{-1} к зашифрованному блоку
   - Обнаружение и исправление ошибки с помощью кода Хэмминга
   - Применяется S^{-1} для получения исходного сообщения
        
"""
        text_widget = ctk.CTkTextbox(self.about_tab, wrap="word", font=("Arial", 12))
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        text_widget.insert("1.0", about_text)
        text_widget.configure(state="disabled")
    
    def generate_keys(self):
        global S, S_inv, P, P_inv, G_hat
        S = random_binary_non_singular_matrix(4)
        S_inv = np.linalg.inv(S).astype(int)
        P = generate_permutation_matrix(7)
        P_inv = np.linalg.inv(P).astype(int)
        G_hat = np.transpose(np.mod((S.dot(np.transpose(G))).dot(P), 2))
        self.update_key_display()
        messagebox.showinfo("Успех", "Ключи успешно сгенерированы!")
    
    def update_key_display(self):
        self.public_key_display.delete("1.0", "end")
        self.public_key_display.insert("1.0", f"{np.array2string(G_hat, precision=0, suppress_small=True)}")
        
        self.private_key_display.delete("1.0", "end")
        private_text = f"Матрица S:\n{np.array2string(S, precision=0, suppress_small=True)}\n\n"
        private_text += f"Матрица P:\n{np.array2string(P, precision=0, suppress_small=True)}"
        self.private_key_display.insert("1.0", private_text)
    
    def select_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.current_file = filename
            self.file_label.configure(text=f"Выбран файл: {os.path.basename(filename)}")
    
    def encrypt_file_gui(self):
        if not self.current_file:
            messagebox.showwarning("Предупреждение", "Сначала выберите файл!")
            return
        
        output_file = filedialog.asksaveasfilename(
            defaultextension=".mceliece",
            filetypes=[("McEliece files", "*.mceliece"), ("All files", "*.*")]
        )
        if output_file:
            self.progress_bar.set(0)
            self.status_label.configure(text="Шифрование...")
            threading.Thread(target=self.encrypt_thread, args=(self.current_file, output_file), daemon=True).start()
    
    def encrypt_thread(self, input_file, output_file):
        try:
            with open(input_file, "rb") as f:
                text = f.read()
            binary_str = ''.join(format(x, '08b') for x in text)
            split_bits_list = split_binary_string(binary_str, 4)
            enc_msg = []
            for i, split_bits in enumerate(split_bits_list):
                enc_bits = hamming7_4_encode(split_bits, G_hat)
                
                err_enc_bits = add_single_bit_error(enc_bits)
                enc_msg.append(''.join(str(x) for x in err_enc_bits))
                self.progress_bar.set((i+1)/len(split_bits_list))
            
            encoded = ''.join(enc_msg)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(encoded)
            
            self.status_label.configure(text="Шифрование завершено")
            messagebox.showinfo("Успех", "Файл успешно зашифрован!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка шифрования: {str(e)}")
    
    def decrypt_file_gui(self):
        if not self.current_file:
            messagebox.showwarning("Предупреждение", "Сначала выберите файл!")
            return
        
        output_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if output_file:
            self.progress_bar.set(0)
            self.status_label.configure(text="Дешифрование...")
            threading.Thread(target=self.decrypt_thread, args=(self.current_file, output_file), daemon=True).start()
    
    def decrypt_thread(self, input_file, output_file):
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                enc_text = f.read()
            split_enc_list = split_binary_string(enc_text, 7)
            dec_msg = []
            for i, enc_bits_str in enumerate(split_enc_list):
                enc_bits = np.array([int(x) for x in enc_bits_str])
                c_hat = np.mod(enc_bits.dot(P_inv), 2)
                err_idx = detect_error(c_hat)
                flip_bit(c_hat, err_idx)
                m_hat = hamming7_4_decode(c_hat)
                m_out = np.mod(m_hat.dot(S_inv), 2)
                dec_msg.append(''.join(str(x) for x in m_out))
                self.progress_bar.set((i+1)/len(split_enc_list))
            
            dec_msg_str = ''.join(dec_msg)
            txt = bits_to_str(dec_msg_str)
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(txt)
            
            self.status_label.configure(text="Дешифрование завершено")
            messagebox.showinfo("Успех", "Файл успешно расшифрован!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка дешифрования: {str(e)}")


if __name__ == "__main__":
    app = McElieceApp()
    app.mainloop()
