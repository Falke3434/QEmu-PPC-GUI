import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import zipfile

# Globale Variable für den 7-Zip-Pfad
seven_zip_path = ''

def select_seven_zip():
    global seven_zip_path
    seven_zip_path = filedialog.askopenfilename(title="Select 7z.exe", filetypes=[("7-Zip Executable", "7z.exe")])
    seven_zip_entry.delete(0, tk.END)
    seven_zip_entry.insert(0, seven_zip_path)

def select_iso_file():
    iso_file = filedialog.askopenfilename(title="Select ISO-File", filetypes=[("ISO-Dateien", "*InstallCD-*.iso")])
    iso_entry.delete(0, tk.END)
    iso_entry.insert(0, iso_file)

def select_lha_file_1():
    lha_file = filedialog.askopenfilename(title="Select LHA-Archive", filetypes=[("LHA-Dateien", "AmigaOS4.1FinalEditionUpdate2-53.14.lha")])
    lha_entry_1.delete(0, tk.END)
    lha_entry_1.insert(0, lha_file)

def select_lha_file_2():
    lha_file = filedialog.askopenfilename(title="Select LHA-Archive", filetypes=[("LHA-Dateien", "siliconmotion502_chip.lha")])
    lha_entry_2.delete(0, tk.END)
    lha_entry_2.insert(0, lha_file)

def select_temp_folder():
    temp_folder = filedialog.askdirectory(title="Select Temp-Folder")
    temp_entry.delete(0, tk.END)
    temp_entry.insert(0, temp_folder)

def add_to_kicklayout(kickstart_folder):
    kicklayout_path = os.path.join(kickstart_folder, 'Kicklayout')
    line_to_add = "MODULE Kickstart/siliconmotion502.chip"
    
    try:
        with open(kicklayout_path, 'a') as kicklayout_file:
            kicklayout_file.write(f"\n{line_to_add}")
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Hinzufügen zur Kicklayout-Datei: {e}")

def create_zip_from_kickstart(kickstart_folder, temp_folder):
    zip_file_path = os.path.join(temp_folder, 'kickstart.zip')
    
    try:
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as kickstart_zip:
            for foldername, subfolders, filenames in os.walk(kickstart_folder):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    kickstart_zip.write(file_path, os.path.relpath(file_path, os.path.dirname(kickstart_folder)))
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Erstellen der ZIP-Datei: {e}")

def delete_files_in_folder_except(folder, exception_file):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if filename != exception_file:
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen von {file_path}: {e}")

def copy_file(src, dest):
    try:
        if os.path.exists(dest):
            os.remove(dest)  # Bestehende Datei löschen
        shutil.copy2(src, dest)  # Datei kopieren
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Kopieren von {src} nach {dest}: {e}")

def create():
    iso_file = iso_entry.get()
    lha_file_1 = lha_entry_1.get()
    lha_file_2 = lha_entry_2.get()
    temp_folder = temp_entry.get()
    
    if not os.path.isfile(seven_zip_path):
        messagebox.showerror("Fehler", "Bitte wähle eine gültige 7-Zip-Executable.")
        return
    
    if not os.path.isfile(iso_file):
        messagebox.showerror("Fehler", "Bitte wähle eine gültige ISO-Datei.")
        return

    if not os.path.isfile(lha_file_1) and not os.path.isfile(lha_file_2):
        messagebox.showerror("Fehler", "Bitte wähle mindestens ein gültiges LHA-Archiv.")
        return

    if not os.path.isdir(temp_folder):
        messagebox.showerror("Fehler", "Bitte wähle einen gültigen Temp-Ordner.")
        return

    try:
        # ISO entpacken
        subprocess.run([seven_zip_path, 'x', iso_file, f'-o{temp_folder}', '-y'], check=True)
        
        # LHA-Archive entpacken
        if os.path.isfile(lha_file_1):
            subprocess.run([seven_zip_path, 'x', lha_file_1, f'-o{temp_folder}', '-y'], check=True)

        if os.path.isfile(lha_file_2):
            subprocess.run([seven_zip_path, 'x', lha_file_2, f'-o{temp_folder}', '-y'], check=True)

        # Kickstart-Ordner festlegen
        kickstart_folder = os.path.join(temp_folder, 'system', 'Kickstart')
        if not os.path.exists(kickstart_folder):
            messagebox.showerror("Fehler", "Kickstart-Ordner nicht gefunden.")
            return

        # Kickstart-Dateien kopieren
        # Kernel von AmigaOS 4.1 FE Update 2 nach Kickstart kopieren
        kernel_source = os.path.join(temp_folder, 'AmigaOS 4.1 Final Edition Update 2', 'Content', 'KickstartPeg2', 'kernel')
        kernel_dest = os.path.join(kickstart_folder, 'kernel')
        copy_file(kernel_source, kernel_dest)

        # siliconmotion502.chip von KickstartSam460 nach Kickstart kopieren
        siliconmotion_source = os.path.join(temp_folder, 'KickstartSam460', 'siliconmotion502.chip')
        siliconmotion_dest = os.path.join(kickstart_folder, 'siliconmotion502.chip')
        copy_file(siliconmotion_source, siliconmotion_dest)

        # Zeile zur Kicklayout-Datei hinzufügen
        add_to_kicklayout(kickstart_folder)

        # Kickstart-Ordner in eine ZIP-Datei komprimieren
        create_zip_from_kickstart(kickstart_folder, temp_folder)

        # Alle Dateien im Temp-Ordner löschen, außer der kickstart.zip
        delete_files_in_folder_except(temp_folder, 'kickstart.zip')

        messagebox.showinfo("Erfolg", "Die Dateien wurden erfolgreich entpackt, die Kicklayout-Datei aktualisiert und die kickstart.zip erstellt.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Fehler", f"Fehler beim Entpacken: {e}")
    except FileNotFoundError as e:
        messagebox.showerror("Fehler", f"7-Zip nicht gefunden: {e}")
    except Exception as e:
        messagebox.showerror("Fehler", f"Ein unerwarteter Fehler ist aufgetreten: {e}")

# GUI erstellen
root = tk.Tk()
root.title("Pegasos2 Kickstart Creator")

# 7-Zip Auswahl
seven_zip_label = tk.Label(root, text="7-Zip Executable:")
seven_zip_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
seven_zip_entry = tk.Entry(root, width=50)
seven_zip_entry.grid(row=0, column=1, padx=5, pady=5)
seven_zip_button = tk.Button(root, text="Browse", command=select_seven_zip)
seven_zip_button.grid(row=0, column=2, padx=5, pady=5)

# ISO-Datei Auswahl
iso_label = tk.Label(root, text="AmigaOS 4.1 ISO-File:")
iso_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
iso_entry = tk.Entry(root, width=50)
iso_entry.grid(row=1, column=1, padx=5, pady=5)
iso_button = tk.Button(root, text="Browse", command=select_iso_file)
iso_button.grid(row=1, column=2, padx=5, pady=5)

# LHA-Datei 1 Auswahl
lha_label_1 = tk.Label(root, text="Update 2 Archive:")
lha_label_1.grid(row=2, column=0, sticky='w', padx=5, pady=5)
lha_entry_1 = tk.Entry(root, width=50)
lha_entry_1.grid(row=2, column=1, padx=5, pady=5)
lha_button_1 = tk.Button(root, text="Browse", command=select_lha_file_1)
lha_button_1.grid(row=2, column=2, padx=5, pady=5)

# LHA-Datei 2 Auswahl
lha_label_2 = tk.Label(root, text="SiliconMotion Archive:")
lha_label_2.grid(row=3, column=0, sticky='w', padx=5, pady=5)
lha_entry_2 = tk.Entry(root, width=50)
lha_entry_2.grid(row=3, column=1, padx=5, pady=5)
lha_button_2 = tk.Button(root, text="Browse", command=select_lha_file_2)
lha_button_2.grid(row=3, column=2, padx=5, pady=5)

# Temp-Ordner Auswahl
temp_label = tk.Label(root, text="Temp-Folder:")
temp_label.grid(row=4, column=0, sticky='w', padx=5, pady=5)
temp_entry = tk.Entry(root, width=50)
temp_entry.grid(row=4, column=1, padx=5, pady=5)
temp_button = tk.Button(root, text="Browse", command=select_temp_folder)
temp_button.grid(row=4, column=2, padx=5, pady=5)

# Create Button
create_button = tk.Button(root, text="Create Kickstart", command=create)
create_button.grid(row=5, columnspan=3, pady=10)

# GUI starten
root.mainloop()
