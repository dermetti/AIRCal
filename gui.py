import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
from AIRCal import *

class Schedule:
    def __init__(self, name=None, pdf_file=None, table=None, month=None, year=None, names=None, index=None, shifts=None, bad_shifts=None):
        self.name = name
        self.pdf_file = pdf_file
        self.table = table
        self.month = month
        self.year = year
        self.names = names
        self.index = index
        self.shifts = shifts
        self.bad_shifts = bad_shifts

schedule = Schedule()



def app():

    # create window
    window = tk.Tk()
    window.title("AIRCal")
    window.geometry("600x400")
    window.resizable(False, False)
    window.columnconfigure(0, weight=1)

    # crate frames
    frame1 = ttk.Frame(window) # name and file
    frame2 = ttk.Frame(window) # error message
    frame3 = ttk.Frame(window) # name manual selection
    frame4 = ttk.Frame(window)
    frame5 = ttk.Frame(window)

    # Tk variables
    current_var = tk.StringVar()

    # place frame
    frame1.grid(row=0, column=0)
    frame2.grid(row=1, column=0)

    # create widgets
    greeting = tk.Label(frame1, text="Name und Dienstplan eingeben", font=("Helvetica", 20))
    name_input_label = tk.Label(frame1, text="Ihr Name wie am Dienstplan", font=("Helvetica", 10))
    name_input = tk.Entry(frame1)
    file_input = ttk.Button(frame1, text="Dienstplan öffnen", command=lambda: open_file(file_path, analyze_btn))
    file_path = tk.Label(frame1, text=f"Datei: nicht angegeben", font=("Helvetica", 10), bg="white")
    analyze_btn = ttk.Button(frame1, text="Scannen", command=lambda: analyze(name_input, error_message, frame1, frame3, namebox), state="disabled")
    error_message = tk.Label(frame2, text="", fg="red")
    namebox = ttk.Combobox(frame3, textvariable=current_var)
    namebox['state'] = 'readonly'
    name_input_btn = ttk.Button(frame3, text="Bestätigen", command=lambda: get_name(frame3, namebox, error_message))

    # place widgets
    greeting.grid(row=0, column=0, columnspan=2, pady=20, padx=20)
    file_input.grid(row=2, column=0, columnspan=2, pady=10)
    name_input_label.grid(row=1, column=0)
    name_input.grid(row=1, column=1, pady=10)
    file_path.grid(row=3, column=0, columnspan=2, pady=10)
    analyze_btn.grid(row=4, column=0, columnspan=2, pady=10)
    error_message.grid(row=5, column=0, columnspan=2, pady=10)
    namebox.pack(pady=10)
    name_input_btn.pack(pady=10)

    
    window.mainloop()
    


def open_file(file_path, analyze_btn):
    schedule.pdf_file = fd.askopenfilename(title="Dienstplan öffnen", initialdir="/", filetypes=[("PDF Datei", "*.pdf")])
    file_path.configure(text = f"Datei: {schedule.pdf_file}")
    if schedule.pdf_file[-4:] == ".pdf":
        analyze_btn["state"] = "normal"


def analyze(name_input, error_message, frame1, frame3, namebox):
    if name_input.get() == "":
        error_message["text"] = "Fehler: Name nicht angegeben"
    else:
        error_message["text"] = ""
        schedule.name = name_input.get()
        schedule.table, schedule.month, schedule.year, schedule.names, = parse_pdf(schedule.pdf_file)
        namebox["values"] = schedule.names
        if not schedule.table or not schedule.month or not schedule.year or not schedule.names:
            error_message["text"] = "Fehler: PDF kann nicht gelesen werden"
        else:
            name_check(frame1, frame3, error_message)


def name_check(frame1, frame3, error_message):
    schedule.index = check_name(schedule.name, schedule.names)
    if not schedule.index:
        frame1.grid_forget()
        frame3.grid(row=0, column=0)
        error_message["text"] = "Ihr Name konnte nicht gefunden werden, bitte auswählen"
    else:
        frame1.grid_forget()
        error_message["text"] = ""
        schedule.shifts, schedule.bad_shifts = extract_schedule(schedule.table, schedule.index)
        data_checker()


def get_name(frame3, namebox, error_message):
    if namebox.get():
        schedule.name = namebox.get()
        error_message["text"] = ""
        frame3.grid_forget()
        schedule.index = check_name(schedule.name, schedule.names)
        schedule.shifts, schedule.bad_shifts = extract_schedule(schedule.table, schedule.index)
        data_checker()

    else:
        error_message["text"] = "Bitte Name auswählen"
    

def data_checker():
    if schedule.bad_shifts:
        pass


if __name__ == "__main__":
    app()