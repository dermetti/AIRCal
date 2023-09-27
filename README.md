# shiftparse
## Video Demo:  <URL HERE>
## Description:

### Basic Overview:
Shiftparse is a program that will extract a shift schedule for a specific person from a PDF that contains the schedule of multiple coworkers in a tabular form. Shiftparse can export the individual schedule of a coworker as a PDF and/or an ICS file.

### Requirements:
The PDF will need to adhere to a specific layout.
The PDF will need to contain a line like "Schedule MONTH YEAR", while MONTH will need to be a word and YEAR a four-digit number.
The schedule for all coworkers needs to contained in a table. Rows will need to contain from left to right: name of coworker, one empty cell, shift assignment for each day of the month (one cell per day)
The first row of the table needs to contain from left to right: two empty cells, number of the day of the month followed by a period ("1." or "2.", etc)
Shiftparse will need to know the abbreviations of all possible shifts such as they appear in the PDF as well as their start and end times. This is to allow for error correction of misspelled shift assignments and to create an individual ICS file for each coworker.

### Executing shiftparse:
To execute shiftparse from the command line type: `python project.py shedule.pdf` where shedule.pdf is the PDF file with the schedule that you want to extract an individual schedule from.
Shiftparse will take a second to parse the PDF file. Shiftparse will check if the PDF contains a valid month and year and prompt the user to input that information if it may be erroneous.
You will then be prompted to input your name. Shiftparse will check if your name is on the schedule and check if on each day of the month a valid shift is assigned. Shiftparse will prompt you to input a valid shift for each day that has an invalid or no shift assigned. Shiftparse will perform basic error checking and corrections if possible.
Siftparse will then output a table with your individual schedule in the terminal and ask for confirmation, that the data extracted is indeed correct.
After confirmation that the data shiftparse has extracted is correct shiftparse will ask you if you want to export the data as an individual PDF schedule, an ICS file or both.

## Functions in shiftparse:

### parse_pdf():
The parse_pdf() function takes as single argument the PDF file as specified in sys.argv[1]. The function uses [pdfplumber](https://pypi.org/project/pdfplumber/) to parse the PDF file and extract/return the table containing the schedule, the month and year as found in the PDF file, a list of all names found in the PDF file (the first column in the table), a list of days as found in the PDF file (the first row in the table).

### check_date():
The check_date() function takes as arguments the month and year as found in the PDF file (returned by parse_pdf()). The function checks if the month argument is a valid english month and prompts the user to manually correct this if necessary. The function then checks if the year argument is the current year or the next year (using [datetime](https://docs.python.org/3/library/datetime.html#module-datetime)) and prompts the user to manually correct this if necessary.

### extract_schedule():
The extract_schedule() function takes as arguments the name of the user (via input()) as well as the table containing the schedule, the list of all names and the list of days returned from parse_pdf(). The function first checks if the name input from the user is in the list of all names. The function then calls the check_data() function which validates and corrects the data found in the row of the table starting with the users name.
After receiving the validated data from check_data(), the function prints the individual schedule of the user using [tabulate](https://pypi.org/project/tabulate/). The user is then prompted to confirm that the data is correct. The function will return the validated list of shifts (the individual schedule) and the name of the user.

### check_data():
The check_data() function takes as arguments the list of shifts found in the table containing the schedule in the row with the name of the user and the list of days found in the PDF file. The function will then go through each shift assignment day by day and check if it is a valid shift assignment. If that is not the case, the function will try simple error correction for common problems (e.g. the shift assignment is in lower instead of upper case). If this is unsuccessful the function will prompt the user to input a valid shift assignment for that specific day.
The function will return the validated list of shifts (the individual schedule).

### exporter():
The exporter() function takes as arguments the validated list of shifts, the list of days, the name of the user, the validated month and year. The function will prompt the user to export the data as an individual PDF schedule, an ICS file or both.
The function will then call pdf_exporter() and ics_exporter() if applicable.

### ics_exporter():
The ics_exporter() function takes as arguments the validated list of shifts, the name of the user, the validated month and year. A calendar is created using [Ics.py]( https://pypi.org/project/ics/). Each shift is added to the calendar as an event. Days off ("x" shifts) are not added. Shifts that have no associated start and end times are added as full day events. Shifts with start and end times have these times converted to a [datetime](https://docs.python.org/3/library/datetime.html#module-datetime) object which is then converted to UTC with [pytz](https://pypi.org/project/pytz/). These shifts are then added as events with a start and end time.
The .ics file is then named as "Schedule_{user_name}\_{month}_{year}.ics" and exported.

### pdf_exporter():
The pdf_exporter() function takes as arguments the validated list of shifts, the list of days, the name of the user, the validated month and year. Using [fpdf2]( https://pypi.org/project/fpdf2/) a PDF file is created with the individual schedule of the user and a legend containing the abbreviations of the shifts the user is assigned to as well as their start and end times (shifts with no associated times are ignored).
The PDF file is then named as "Schedule_{user_name}\_{month}_{year}.pdf" and exported.
