import pdfplumber
from tabulate import tabulate
import re
from fpdf import FPDF
from ics import Calendar, Event
from datetime import datetime, date, timedelta
import pytz
import sys


allowed_shifts = {'*9': [],
                  '*C': [],
                  'AK': ["07:00", "16:00"],
                  'BH': ["07:30", "20:15"],
                  'BN': ["19:30", "08:00"],
                  'BO': ["07:30", "16:00"],
                  'BT': ["07:30", "20:00"],
                  'DP': ["07:30", "20:00"],
                  'EZ': [],
                  'F3': ["09:00", "12:30"],
                  'IH': ["07:30", "20:15"],
                  'IN': ["19:00", "07:45"],
                  'IO': ["07:00", "16:00"],
                  'IS': ["07:00", "15:30"],
                  'IT': ["07:00", "19:45"],
                  'IW': [],
                  'KA': ["08:00", "16:00"],
                  'KS': ["09:00", "17:30"],
                  'N1': ["19:30", "07:45"],
                  'N2': ["19:30", "07:45"],
                  'NN': ["19:30", "07:45"],
                  'NO': ["07:30", "16:00"],
                  'NR': ["07:45", "16:15"],
                  'NS': ["11:30", "20:00"],
                  'NT': ["07:30", "19:45"],
                  'NÄ': ["07:30", "16:00"],
                  'T1': ["07:30", "20:00"],
                  'T2': ["07:30", "20:00"],
                  'TB': ["07:00", "15:30"],
                  'U': [],
                  'x': []

}
months_eng = {
    "January": "01",
    "February": "02",
    "March": "03",
    "April": "04",
    "May": "05",
    "June": "06",
    "July": "07",
    "August": "08",
    "September": "09",
    "October": "10",
    "November": "11",
    "December": "12"

}

# main function
def main():
    table, month_raw, year_raw, names, dates = parse_pdf(sys.argv[1])
    month, year = check_date(month_raw, year_raw)
    schedule, name = extract_schedule(input("What is your name? ").strip().title(), table, names, dates)
    exporter(schedule, dates, name, month, year)



# parser with pdfplumber
def parse_pdf(f):
    try:
        with pdfplumber.open(f) as pdf:
            page = pdf.pages[0]
            table = page.extract_table({"vertical_strategy": "lines", "horizontal_strategy": "lines"})
            text = page.extract_text_simple(x_tolerance=3, y_tolerance=3)
            matches = re.search(r"Schedule (\w.+) (\d{4})", text)
            dates = table[0][2:]
            names = []
            for line in table[2:]:
                names.append(line[0])
            month_raw, year_raw = matches.groups()
            return table, month_raw, year_raw, names, dates
    except:
        sys.exit("File does not exist or is not a pdf")


def check_date(month, year):
    curr_year = date.today().year
    if month not in months_eng:
        while True:
            month = input(f"Month | {month} | is wrong, input correct month of schedule: ").title().strip()
            if month in months_eng:
                break
            else:
                continue
    if year != str(curr_year) and year != str(curr_year + 1):
        while True:
            y = input(f"Year | {year} | may be wrong, input correct year of schedule: ").strip()
            if len(y) == 4 and y.isdigit():
                year = int(y)
                break
            else:
                continue
    return month, year


def extract_schedule(name, t, names, dates):
    if name not in names:
        print("An error has occured, let's try again")
        main()
    for line in t:
        if name == line[0]:
            shifts = check_data(line[2:], dates)
            print(tabulate([shifts], headers=dates, tablefmt="rounded_grid"))
            while True:
                answer = input("Does this look correct? [y/n] ").strip().casefold()
                if answer == "y":
                    return shifts, name
                elif answer == "n":
                    print("An error has occured, let's try again")
                    main()
                else:
                    continue


def check_data(shifts, days):
    i = -1
    for shift in shifts:
        i += 1
        if shift not in allowed_shifts:
            while True:
                if shift[0:2] in allowed_shifts:
                    corr_shift = shift[0:2]
                    break
                elif shift[0:1] in allowed_shifts:
                    corr_shift = shift[0:1]
                    break
                elif shift.upper() in allowed_shifts:
                    corr_shift = shift.upper()
                    break
                corr_shift = input(f"Shift | {shift} | on the {days[i]} is not correct. What is your shift on that day? ")
                if corr_shift in allowed_shifts:
                    break
                elif corr_shift.upper() in allowed_shifts:
                    corr_shift = corr_shift.upper()
                    break
                else:
                    continue
            shifts[i] = corr_shift
    return shifts


def exporter(schedule, dates, name, month, year):
    while True:
        export_options = input("Do you want to export your schedule as a PDF [p], ICS [i] or both [b]? ").casefold().strip()
        if export_options in ["p", "i", "b"]:
            break
        else:
            continue
    if export_options == "p":
        pdf_exporter(schedule, dates, name, month, year)
    elif export_options == "i":
        ics_exporter(schedule, name, month, year)
    elif export_options == "b":
        pdf_exporter(schedule, dates, name, month, year)
        ics_exporter(schedule, name, month, year)


def ics_exporter(schedule, name, month, year):
    c = Calendar(creator="shiftparse")
    i = 1
    local = pytz.timezone("Europe/Berlin")
    now = datetime.now()
    for shift in schedule:
        if shift == "x":
            i += 1
            continue
        else:
            e = Event()
            e.name = shift
            if allowed_shifts[shift] != []:
                start = datetime.strptime(f"{year}-{months_eng[month]}-{i:02d} {allowed_shifts[shift][0]}", "%Y-%m-%d %H:%M")
                start_de = local.localize(start, is_dst=None)
                start_utc = start_de.astimezone(pytz.utc)
                end = datetime.strptime(f"{year}-{months_eng[month]}-{i:02d} {allowed_shifts[shift][1]}", "%Y-%m-%d %H:%M")
                end_de = local.localize(end, is_dst=None)
                end_utc = end_de.astimezone(pytz.utc)
                e.created = (now)
                e.begin = f"{start_utc}"
                if start.time() > end.time():
                    end_utc = end_utc + timedelta(days=1)
                    e.end = f"{end_utc}"
                else:
                    e.end = f"{end_utc}"
            else:
                e.begin = f"{year}-{months_eng[month]}-{i:02d} 00:00:00"
                e.created = (now)
                e.make_all_day()
            c.events.add(e)
            i += 1
    with open(f"Schedule_{name}_{month}_{year}.ics", "w") as file:
        file.write(c.serialize())



def pdf_exporter(schedule, dates, name, month, year):
    pdf = FPDF(orientation="L")
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 22)
    pdf.set_y(20)
    pdf.cell(txt=f"Schedule for {name}, {month} {year}", center=True)
    pdf.set_y(70)
    pdf.set_font('helvetica', '', 12)
    data = [dates, schedule]
    with pdf.table(text_align="CENTER", borders_layout="INTERNAL") as table:
        for data_row in data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)
    pdf.set_y(120)
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(txt=f"Legend", center=True)
    pdf.set_y(140)
    pdf.set_font('helvetica', '', 12)
    shifts = list(set(schedule))
    shifts.sort()
    shifts = [i for i in shifts if i not in ["U", "x", "EZ", "IW", "*9", "*C"]]
    width = len(shifts)
    times = []
    for shift in shifts:
        t = allowed_shifts[shift]
        times.append(f"{t[0]} - {t[1]}")
    data = [shifts, times]
    with pdf.table(width=(width * 30), text_align="CENTER", borders_layout="INTERNAL") as table:
        for data_row in data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)
    pdf.output(f"Schedule_{name}_{month}_{year}.pdf")
				  

if __name__=="__main__":
    main()