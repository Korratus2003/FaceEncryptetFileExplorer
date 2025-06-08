import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from encryption import encrypt_file, decrypt_file
from biometrics import recognize_face
import threading

class FileExplorer(TkinterDnD.Tk):
    def __init__(self, biometric_key_hex: str):
        super().__init__()
        self.biometric_key_hex = biometric_key_hex
        self.title("Bezpieczny Eksplorator Plików (Tkinter DnD)")
        self.geometry("600x400")

        self.label = tk.Label(self, text="Przeciągnij pliki tutaj, aby zaszyfrować lub odszyfrować")
        self.label.pack(pady=10)

        self.listbox = tk.Listbox(self, width=80, height=15)
        self.listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind('<<Drop>>', self.drop)

    def drop(self, event):
        files = self.tk.splitlist(event.data)
        threading.Thread(target=self.process_files, args=(files,), daemon=True).start()

    def process_files(self, files):
        for file_path in files:
            try:
                try:
                    out_path = decrypt_file(file_path, self.biometric_key_hex)
                    self._append_listbox(f"Odszyfrowano: {file_path} -> {out_path}")
                except Exception:
                    out_path = encrypt_file(file_path, self.biometric_key_hex)
                    self._append_listbox(f"Zaszyfrowano: {file_path} -> {out_path}")
            except Exception as e:
                self._append_listbox(f"Błąd pliku {file_path}: {str(e)}")

    def _append_listbox(self, text: str):
        self.after(0, lambda: self.listbox.insert(tk.END, text))


def main():
    print("🔐 Autoryzacja biometryczna...")
    recognized, biometric_key = recognize_face()
    if not recognized:
        print("❌ Twarz nie została rozpoznana. Zamykanie.")
        return

    print("✅ Twarz rozpoznana. Uruchamianie eksploratora.")
    app = FileExplorer(biometric_key)
    app.mainloop()


if __name__ == "__main__":
    main()
