import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
from jpeg import encrypt_message, decrypt_message
import threading

class SteganographyApp:
    def __init__(self):
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Скрытие и извлечение сообщений")
        self.root.geometry("1100x700")
        self.root.minsize(1000, 700)
        
        self.center_window()
        
        self.image_path = ""
        self.output_path = "img/output.jpeg"
        self.preview_image = None
        self.current_mode = "encrypt" 
        
        self.setup_ui()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        main_container = ctk.CTkFrame(self.root, corner_radius=15)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Steganography Laboratory",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#2E86AB"
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Скрытие и извлечение сообщений в изображениях с использованием DCT",
            font=ctk.CTkFont(size=14),
            text_color="#A8DADC"
        )
        subtitle_label.pack(pady=(5, 0))
        
        mode_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        mode_frame.pack(pady=10)
        
        self.mode_var = ctk.StringVar(value="encrypt")
        encrypt_radio = ctk.CTkRadioButton(
            mode_frame, 
            text="Режим шифрования", 
            variable=self.mode_var, 
            value="encrypt",
            command=self.switch_mode,
            font=ctk.CTkFont(weight="bold")
        )
        encrypt_radio.pack(side="left", padx=20)
        
        decrypt_radio = ctk.CTkRadioButton(
            mode_frame, 
            text="Режим расшифровки", 
            variable=self.mode_var, 
            value="decrypt",
            command=self.switch_mode,
            font=ctk.CTkFont(weight="bold")
        )
        decrypt_radio.pack(side="left", padx=20)
        
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        left_column = ctk.CTkFrame(content_frame, corner_radius=10)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_column = ctk.CTkFrame(content_frame, corner_radius=10)
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
                
        image_section = ctk.CTkFrame(left_column, corner_radius=10)
        image_section.pack(fill="x", pady=(0, 15))
        
        section_title1 = ctk.CTkLabel(
            image_section,
            text="Выбор изображения",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        section_title1.pack(anchor="w", padx=15, pady=(15, 10))
        
        image_path_frame = ctk.CTkFrame(image_section, fg_color="transparent")
        image_path_frame.pack(fill="x", padx=15, pady=5)
        
        self.image_entry = ctk.CTkEntry(
            image_path_frame,
            placeholder_text="Выберите изображение...",
            height=35
        )
        self.image_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            image_path_frame,
            text="Обзор",
            width=80,
            height=35,
            command=self.browse_image,
            fg_color="#2E86AB",
            hover_color="#1B6B93"
        )
        browse_btn.pack(side="right")
        
        self.message_section = ctk.CTkFrame(left_column, corner_radius=10)
        self.message_section.pack(fill="both", expand=True, pady=(0, 15))
        
        section_title2 = ctk.CTkLabel(
            self.message_section,
            text="Сообщение для скрытия",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        section_title2.pack(anchor="w", padx=15, pady=(15, 10))
        
        self.message_text = ctk.CTkTextbox(
            self.message_section,
            height=120,
            border_width=1,
            border_color="#565B5E"
        )
        self.message_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        self.decrypt_info_section = ctk.CTkFrame(left_column, corner_radius=10)
        
        section_title_decrypt = ctk.CTkLabel(
            self.decrypt_info_section,
            text="Информация для расшифровки",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        section_title_decrypt.pack(anchor="w", padx=15, pady=(15, 10))
        
        decrypt_info_text = ctk.CTkTextbox(
            self.decrypt_info_section,
            height=120,
            border_width=1,
            border_color="#565B5E",
            state="disabled"
        )
        decrypt_info_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        info_content = """Программа автоматически определит и извлечёт скрытое сообщение из выбранного изображения.

Для успешной расшифровки:
• Изображение должно содержать скрытое сообщение
• Формат должен быть JPEG

Просто выберите изображение и нажмите "Расшифровать сообщение"."""
        
        decrypt_info_text.configure(state="normal")
        decrypt_info_text.insert("1.0", info_content)
        decrypt_info_text.configure(state="disabled")
        
        self.output_section = ctk.CTkFrame(left_column, corner_radius=10)
        self.output_section.pack(fill="x", pady=(0, 15))
        
        section_title3 = ctk.CTkLabel(
            self.output_section,
            text="Сохранение результата",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        section_title3.pack(anchor="w", padx=15, pady=(15, 10))
        
        output_path_frame = ctk.CTkFrame(self.output_section, fg_color="transparent")
        output_path_frame.pack(fill="x", padx=15, pady=5)
        
        self.output_entry = ctk.CTkEntry(
            output_path_frame,
            placeholder_text="Путь для сохранения...",
            height=35
        )
        self.output_entry.insert(0, self.output_path)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_output_btn = ctk.CTkButton(
            output_path_frame,
            text="Обзор",
            width=80,
            height=35,
            command=self.browse_output,
            fg_color="#2E86AB",
            hover_color="#1B6B93"
        )
        browse_output_btn.pack(side="right")
        
        button_frame = ctk.CTkFrame(left_column, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)
        
        self.action_btn = ctk.CTkButton(
            button_frame,
            text="Зашифровать сообщение",
            height=50,
            command=self.perform_action,
            fg_color="#27AE60",
            hover_color="#219653",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.action_btn.pack(fill="x", pady=5)
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Очистить все",
            height=40,
            command=self.clear_all,
            fg_color="#95A5A6",
            hover_color="#7F8C8D",
            font=ctk.CTkFont(size=13)
        )
        clear_btn.pack(fill="x", pady=5)
        
        preview_section = ctk.CTkFrame(right_column, corner_radius=10)
        preview_section.pack(fill="both", expand=True, pady=(0, 15))
        
        section_title4 = ctk.CTkLabel(
            preview_section,
            text="Превью изображения",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        section_title4.pack(anchor="w", padx=15, pady=(15, 10))
        
        self.preview_frame = ctk.CTkFrame(preview_section, fg_color="#1A1A1A", corner_radius=8)
        self.preview_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Изображение не выбрано\n\nВыберите изображение для просмотра",
            text_color="#7F8C8D",
            font=ctk.CTkFont(size=12),
            justify="center"
        )
        self.preview_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        result_section = ctk.CTkFrame(right_column, corner_radius=10)
        result_section.pack(fill="both", expand=True)
        
        section_title5 = ctk.CTkLabel(
            result_section,
            text="Результат",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        section_title5.pack(anchor="w", padx=15, pady=(15, 10))
        
        self.result_text = ctk.CTkTextbox(
            result_section,
            height=200,
            border_width=1,
            border_color="#565B5E",
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.result_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.status_var = ctk.StringVar(value="Готов к работе - выберите режим")
        status_bar = ctk.CTkFrame(main_container, fg_color="transparent")
        status_bar.pack(fill="x", padx=20, pady=(10, 0))
        
        status_label = ctk.CTkLabel(
            status_bar,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12),
            text_color="#A8DADC"
        )
        status_label.pack(side="left")
        
        self.progress_bar = ctk.CTkProgressBar(status_bar, height=3, width=200)
        self.progress_bar.pack(side="right")
        self.progress_bar.set(0)
        
        self.switch_mode()
        
    def switch_mode(self):
        self.current_mode = self.mode_var.get()
        
        if self.current_mode == "encrypt":
            self.message_section.pack(fill="both", expand=True, pady=(0, 15))
            self.output_section.pack(fill="x", pady=(0, 15))
            self.decrypt_info_section.pack_forget()
            
            self.action_btn.configure(
                text="Зашифровать сообщение",
                fg_color="#27AE60",
                hover_color="#219653"
            )
            self.status_var.set("Режим шифрования - введите сообщение и выберите изображение")
            
        else:  
            self.message_section.pack_forget()
            self.output_section.pack_forget()
            self.decrypt_info_section.pack(fill="both", expand=True, pady=(0, 15))
            
            self.action_btn.configure(
                text="Расшифровать сообщение",
                fg_color="#E74C3C",
                hover_color="#C0392B"
            )
            self.status_var.set("Режим расшифровки - выберите изображение со скрытым сообщением")
        
    def browse_image(self):
        filename = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Image files", "*.jpg *.jpeg "),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.image_path = filename
            self.image_entry.delete(0, "end")
            self.image_entry.insert(0, filename)
            self.show_image_preview(filename)
            
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Сохранить как",
            defaultextension=".jpeg",
            filetypes=[
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.output_path = filename
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, filename)
            
    def show_image_preview(self, image_path):
        try:
            image = Image.open(image_path)
            max_size = (320, 240)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            
            self.preview_label.configure(
                text="",
                image=photo
            )
            self.preview_label.image = photo  
            
            original_image = Image.open(image_path)
            info_text = f"Размер: {original_image.size[0]}x{original_image.size[1]}\nФормат: {original_image.format}\n"
            
            self.preview_label.configure(text=info_text, compound="top")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")
            
    def perform_action(self):
        if self.current_mode == "encrypt":
            self.encrypt_message()
        else:
            self.decrypt_message()
            
    def encrypt_message(self):
        image_path = self.image_entry.get()
        message = self.message_text.get("1.0", "end").strip()
        output_path = self.output_entry.get()
        
        if not image_path or not os.path.exists(image_path):
            messagebox.showerror("Ошибка", "Пожалуйста, выберите корректный файл изображения")
            return
            
        if not message:
            messagebox.showerror("Ошибка", "Пожалуйста, введите сообщение для скрытия")
            return
            
        thread = threading.Thread(target=self._encrypt_thread, args=(image_path, message, output_path))
        thread.daemon = True
        thread.start()
        
    def _encrypt_thread(self, image_path, message, output_path):
        try:
            self.root.after(0, self._set_ui_state, False)
            self.root.after(0, lambda: self.status_var.set("Шифрование..."))
            self.root.after(0, lambda: self.progress_bar.set(0.3))
            
            encrypt_message(image_path, message, output_path)
            
            self.root.after(0, self._encrypt_success, output_path, message)
            
        except Exception as e:
            self.root.after(0, self._encrypt_error, str(e))
            
    def _encrypt_success(self, output_path, message):
        self.progress_bar.set(1.0)
        
        self.result_text.delete("1.0", "end")
        self.result_text.insert("end", "Сообщение успешно зашифровано!\n\n", "success")
        self.result_text.insert("end", f"Файл: {output_path}\n", "info")
        self.result_text.insert("end", f"Сообщение: {message}\n", "info")
        self.result_text.insert("end", f"Длина: {len(message)} символов\n", "info")
        self.result_text.insert("end", f"Размер: {os.path.getsize(output_path)} байт\n\n", "info")
        self.result_text.insert("end", "Сообщение сохранено в изображении. Теперь вы можете поделиться им!", "tip")
        
        self.result_text.tag_config("success", foreground="#27AE60")
        self.result_text.tag_config("info", foreground="#3498DB")
        self.result_text.tag_config("tip", foreground="#F39C12")
        
        self.status_var.set("Сообщение успешно зашифровано")
        self._set_ui_state(True)
        self.root.after(2000, lambda: self.progress_bar.set(0))
        
    def _encrypt_error(self, error_msg):
        self.progress_bar.set(0)
        detailed_error = f"Произошла ошибка при шифровании:\n{error_msg}"

        messagebox.showerror("Ошибка шифрования", detailed_error)
        self.status_var.set("Ошибка при шифровании")
        self._set_ui_state(True)
        
    def decrypt_message(self):
        image_path = self.image_entry.get()
        
        if not image_path or not os.path.exists(image_path):
            messagebox.showerror("Ошибка", "Пожалуйста, выберите корректный файл изображения")
            return
            
        thread = threading.Thread(target=self._decrypt_thread, args=(image_path,))
        thread.daemon = True
        thread.start()
        
    def _decrypt_thread(self, image_path):
        try:
            self.root.after(0, self._set_ui_state, False)
            self.root.after(0, lambda: self.status_var.set("Поиск скрытого сообщения..."))
            self.root.after(0, lambda: self.progress_bar.set(0.3))
            
            recovered_text = decrypt_message(image_path)
            
            self.root.after(0, self._decrypt_success, recovered_text, image_path)
            
        except Exception as e:
            self.root.after(0, self._decrypt_error, str(e))
            
    def _decrypt_success(self, recovered_text, image_path):
        self.progress_bar.set(1.0)
        
        self.result_text.delete("1.0", "end")
        
        if recovered_text and not recovered_text.startswith("[") and not "Ошибка" in recovered_text:
            self.result_text.insert("end", "Сообщение успешно извлечено!\n\n", "success")
            self.result_text.insert("end", f"Текст сообщения:\n", "header")
            self.result_text.insert("end", f"{recovered_text}\n\n", "message")
            self.result_text.insert("end", f"Длина: {len(recovered_text)} символов\n", "info")
            self.result_text.insert("end", f"Источник: {os.path.basename(image_path)}\n", "info")
        else:
            self.result_text.insert("end", "Сообщение не найдено\n\n", "error")
            self.result_text.insert("end", "В выбранном изображении не обнаружено скрытого сообщения.\n\n", "info")
            self.result_text.insert("end", "Возможные причины:\n", "header")
            self.result_text.insert("end", "• Изображение не содержит скрытого сообщения\n")
            self.result_text.insert("end", "• Сообщение было повреждено\n")
            self.result_text.insert("end", "• Использован другой метод стеганографии\n")
        
        self.result_text.tag_config("success", foreground="#27AE60")
        self.result_text.tag_config("error", foreground="#E74C3C")
        self.result_text.tag_config("info", foreground="#3498DB")
        self.result_text.tag_config("header", foreground="#F39C12", font=ctk.CTkFont(weight="bold"))
        self.result_text.tag_config("message", foreground="#FFFFFF", font=ctk.CTkFont(size=13))
        
        self.status_var.set("Расшифровка завершена")
        self._set_ui_state(True)
        self.root.after(2000, lambda: self.progress_bar.set(0))
        
    def _decrypt_error(self, error_msg):
        self.progress_bar.set(0)
        messagebox.showerror("Ошибка расшифровки", f"Произошла ошибка при расшифровке:\n{error_msg}")
        self.status_var.set("Ошибка при расшифровке")
        self._set_ui_state(True)
        
    def _set_ui_state(self, enabled):
        state = "normal" if enabled else "disabled"
        try:
            self.action_btn.configure(state=state)
            self.image_entry.configure(state=state)
            self.output_entry.configure(state=state)
            self.message_text.configure(state=state)
        except Exception as e:
            print(f"Ошибка при обновлении UI: {e}")
        
    def clear_all(self):
        self.image_entry.delete(0, "end")
        self.message_text.delete("1.0", "end")
        self.output_entry.delete(0, "end")
        self.output_entry.insert(0, "img/output.jpeg")
        self.result_text.delete("1.0", "end")
        self.status_var.set(f"Готов к работе - режим {'шифрования' if self.current_mode == 'encrypt' else 'расшифровки'}")
        self.progress_bar.set(0)
        
        mode_text = "шифрования" if self.current_mode == "encrypt" else "расшифровки"
        self.preview_label.configure(
            text=f"Изображение не выбрано\n\nВыберите изображение для {mode_text}",
            image=""
        )
        
        self._set_ui_state(True)
        
    def run(self):
        self.root.mainloop()

def main():
    app = SteganographyApp()
    app.run()

if __name__ == "__main__":
    main()
