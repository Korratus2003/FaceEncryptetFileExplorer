import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from encryption import encrypt_file, decrypt_file
from biometrics import recognize_face, scan_face_multiple_times, save_multiple_reference_data_sqlite, has_biometric_data
import threading

class FileExplorer(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.biometric_key_hex = None
        self.title("Bezpieczny Eksplorator Plików (Tkinter DnD)")
        self.geometry("600x400")

        self.scan_button = tk.Button(self, text="Zeskanuj twarz", command=self.scan_face_or_lock)
        self.scan_button.pack(pady=5)

        self.label = tk.Label(self, text="Przeciągnij pliki tutaj, aby zaszyfrować lub odszyfrować")
        self.label.pack(pady=5)

        self.listbox = tk.Listbox(self, width=80, height=15)
        self.listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind('<<Drop>>', self.drop)

        self.files_enabled = False

    def add_user(self):
        self._append_listbox("🔵 Dodawanie użytkownika - rozpoczęto skanowanie...")
        self.scan_button.config(state=tk.DISABLED)  # blokuj przycisk na czas dodawania
        threading.Thread(target=self.add_user_thread, daemon=True).start()

    def add_user_thread(self):
        scans = scan_face_multiple_times(count=4)
        if scans:
            save_multiple_reference_data_sqlite(scans)
            message = "✅ Użytkownik dodany pomyślnie. Teraz możesz skanować twarz."
        else:
            message = "❌ Nie udało się dodać użytkownika (skan nieudany)."
        self._append_listbox(message)
        self.after(0, lambda: self.scan_button.config(state=tk.NORMAL))  # odblokuj przycisk po zakończeniu

    def scan_face_or_lock(self):
        self.scan_button.config(state=tk.DISABLED)

        # Sprawdź, czy w bazie są dane biometryczne
        if not has_biometric_data():
            self._append_listbox("❗️ Brak danych biometrycznych. Rozpoczynam dodawanie użytkownika...")
            self.add_user()
            return

        if self.files_enabled:
            self.biometric_key_hex = None
            self.files_enabled = False
            self._append_listbox("🔒 Aplikacja zablokowana. Nie można szyfrować/deszyfrować.")
            self.scan_button.config(text="Zeskanuj twarz")
            self.after(2000, lambda: self.scan_button.config(state=tk.NORMAL))
        else:
            self._append_listbox("🔵 Rozpoczynanie rozpoznawania twarzy...")
            threading.Thread(target=self.recognize_face_thread, daemon=True).start()

    def recognize_face_thread(self):
        recognized, biometric_key, message = recognize_face()
        self._append_listbox(("✅" if recognized else "❌") + " " + message)
        if recognized:
            self.biometric_key_hex = biometric_key
            self.files_enabled = True
            self.after(0, lambda: self.scan_button.config(text="Zablokuj"))

        # Odblokuj przycisk skanowania
        self.after(0, lambda: self.scan_button.config(state=tk.NORMAL))

    def drop(self, event):
        if not self.files_enabled:
            self._append_listbox("❌ Najpierw zeskanuj twarz, aby włączyć obsługę plików.")
            return
        files = self.tk.splitlist(event.data)
        threading.Thread(target=self.process_files, args=(files,), daemon=True).start()

    def process_files(self, files):
        for file_path in files:
            try:
                if file_path.lower().endswith('.enc'):
                    # Plik zaszyfrowany - próbujemy odszyfrować
                    try:
                        out_path = decrypt_file(file_path, self.biometric_key_hex)
                        self._append_listbox(f"Odszyfrowano: {file_path} -> {out_path}")
                    except Exception as e:
                        self._append_listbox(f"❌ Nie udało się odszyfrować pliku {file_path}: {str(e)}")
                else:
                    # Plik niezaszyfrowany - szyfrujemy
                    try:
                        out_path = encrypt_file(file_path, self.biometric_key_hex)
                        self._append_listbox(f"Zaszyfrowano: {file_path} -> {out_path}")
                    except Exception as e:
                        self._append_listbox(f"❌ Błąd szyfrowania pliku {file_path}: {str(e)}")

            except Exception as e:
                self._append_listbox(f"❌ Nieoczekiwany błąd pliku {file_path}: {str(e)}")

    def _append_listbox(self, text: str):
        self.after(0, lambda: self.listbox.insert(tk.END, text))


def main():
    app = FileExplorer()
    app.mainloop()


if __name__ == "__main__":
    main()
