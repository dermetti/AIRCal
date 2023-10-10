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
    "Januar": "01",
    "Februar": "02",
    "März": "03",
    "April": "04",
    "Mai": "05",
    "Juni": "06",
    "Juli": "07",
    "August": "08",
    "September": "09",
    "Oktober": "10",
    "November": "11",
    "Dezember": "12"

}

# main function
def main():
    file = "AIR-Dienstplan_2023_11[12022].pdf"
    name = "von Medem"
    table, month, year, names = parse_pdf(file)
    index = check_name(name, names)
    shifts, bad_shifts = extract_schedule(table, index)
    #exporter(schedule, name, month, year)



# parser with pdfplumber
def parse_pdf(f):
    try:
        with pdfplumber.open(f) as pdf:
            page = pdf.pages[0]
            table_raw = page.extract_table({"vertical_strategy": "lines", "horizontal_strategy": "lines"})
            table=[]
            for line in table_raw:
                if line[0]:
                    table.append(line)
            text = page.extract_text_simple(x_tolerance=3, y_tolerance=3)
            matches = re.search(r"Dienstplan (\w.+) (\d{4})", text)
            names = []
            for line in table:
                if line[0]:
                    name = line[0]
                    name = name.casefold()[0:7]
                    if name[0:3] != "von":
                        name = name.split()[0]
                    names.append(name)
            month, year = matches.groups()
            return table, month, year, names
    except:
        return None, None, None, None


def check_name(name, names):

    table_name = name.strip().casefold()[0:7]
    if table_name in names and names.count(table_name) == 1:
        return names.index(table_name)
    else:
        return None
    
    

def extract_schedule(table, index):
    days = []
    for line in table:
        days.append(len(line[4:-2]))
    corr_days = max(set(days), key = days.count)
    shifts = table[index][4:-2]
    if len(shifts) != corr_days:
        print("Nicht alle Tage konnten ausgelesen werden! ")
    shifts, bad_shifts = check_data(shifts)
    return shifts, bad_shifts
    



def check_data(shifts):
    i = -1
    bad_shifts = {}
    for shift in shifts:
        i += 1
        if shift not in allowed_shifts:
            while True:
                if shift[0:2] in allowed_shifts:
                    shifts[i] = shift[0:2]
                    break
                elif shift[0:1] in allowed_shifts:
                    shifts[i] = shift[0:1]
                    break
                elif shift.upper() in allowed_shifts:
                    shifts[i] = shift.upper()
                    break
                else:
                    bad_shifts[(i + 1)] = shift
                    break
    return shifts, bad_shifts




def ics_exporter(shifts, name, month, year):
    c = Calendar(creator="shiftparse")
    i = 1
    local = pytz.timezone("Europe/Berlin")
    now = datetime.now()
    for shift in shifts:
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