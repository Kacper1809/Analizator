from tkinter import *
from Baza import *

baza = Baza()

"""--------------User interface------------------------"""
window = Tk()
window.title("Analyzer")
window.config(padx=50, pady=30, height=800, width=800)

title_label = Label(text="Analyzer", font=("Helvetica", 25))
title_label.grid(column=0, row=0)

buttons_frame = LabelFrame(text="File Buttons")

buttons_frame.grid(column=0, row=1)

master_button = Button(buttons_frame, text="Choose masterdata file", command=baza.open_masterdata)
master_button.grid(pady=10)

measurement_button = Button(buttons_frame, text="Choose measurements file", command=baza.open_measurements)
measurement_button.grid(padx=10, pady=10)

serialnum_frame = LabelFrame(text="S/N")
serialnum_frame.grid(column=0, row=2)

serialnum_Label = Label(serialnum_frame, text="Serial number")
serialnum_Label.grid(row=1)
serialnum_entry = Entry(serialnum_frame, font=("calibre", 10, "normal"))
serialnum_entry.grid(row=2, padx=10)


def button_command():
    serialnumber = serialnum_entry.get()
    baza.select(serialnumber)


submit_button = Button(serialnum_frame, text="Submit", command=button_command)
submit_button.grid(row=3, pady=10)

window.mainloop()
