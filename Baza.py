from tkinter import filedialog
from tkinter import messagebox
import mysql.connector
import csv
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons


class Baza:

    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect_to_database()

    def connect_to_database(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
        )
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS analizatordatabase")
        self.connection.database = "analizatordatabase"

        self.cursor.execute("CREATE TABLE IF NOT EXISTS Devices(serial int PRIMARY KEY,name VARCHAR(50), sap int)")
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Measurements(
                    measurement_id INT AUTO_INCREMENT PRIMARY KEY,
                    serial INT,
                    FOREIGN KEY(serial) REFERENCES Devices(serial),
                    voltage INT,
                    current INT,
                    measurement_time DATETIME
                )
            """)

        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS LogTrigger (
                    record_id INT AUTO_INCREMENT PRIMARY KEY,
                    creation_date DATETIME,
                    serial INT,
                    FOREIGN KEY(serial) REFERENCES Devices(serial)
                )
            """)

        # Usunięcie triggera, jeśli istnieje
        self.cursor.execute("DROP TRIGGER IF EXISTS new_record")

        # Tworzenie triggera
        self.cursor.execute("""
               CREATE TRIGGER new_record
               AFTER INSERT ON Devices
               FOR EACH ROW
               BEGIN
                   INSERT INTO LogTrigger (serial, creation_date)
                   VALUES (NEW.serial, NOW());
               END;
           """)
        self.connection.commit()  # Zatwierdzenie zmian w bazie danych

    def open_masterdata(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        with open(filepath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=";")
            for row in csv_reader:
                try:
                    serial, name, sap = row
                except ValueError:
                    messagebox.showerror("Error", "Invalid data format in the CSV file.")
                    return
                # Sprawdzenie, czy rekord o podanym numerze seryjnym już istnieje
                self.cursor.execute("SELECT COUNT(*) FROM Devices WHERE serial = %s", (serial,))
                count = self.cursor.fetchone()[0]
                if count == 0:  # Jeśli nie ma jeszcze rekordu o takim numerze seryjnym
                    # Wstawienie rekordu do tabeli
                    sql = "INSERT INTO Devices (serial, name, sap) VALUES (%s, %s, %s)"
                    self.cursor.execute(sql, (serial, name, sap))
                    messagebox.showinfo("Success", "Record added successfully")
                else:  # Jeśli rekord o takim numerze seryjnym już istnieje
                    messagebox.showinfo("Duplicate", f"Record with serial number {serial} already exists.")
        self.connection.commit()

    def open_measurements(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        with open(filepath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=";")
            for row in csv_reader:
                try:
                    serial, voltage, current, measurement_time = row
                except ValueError:
                    messagebox.showerror("Error", "Invalid data format in the CSV file.")
                    return
                    # Sprawdzenie, czy numer seryjny istnieje w tabeli Devices
                self.cursor.execute("SELECT COUNT(*) FROM Devices WHERE serial = %s", (serial,))
                count = self.cursor.fetchone()[0]
                if count == 0:
                    messagebox.showerror("Error", f"Serial number {serial} does not exist in Devices table.")
                    return
                sql = "INSERT INTO Measurements (serial, voltage, current, measurement_time) VALUES (%s, %s, %s, %s)"
                self.cursor.execute(sql, (serial, voltage, current, measurement_time))
            messagebox.showinfo("Success", "Record added successfully")
        self.connection.commit()

    def select(self, serialnumber):

        self.cursor.execute("SELECT * FROM Devices d, Measurements m"
                            " WHERE d.serial = m.serial"
                            " AND d.serial = %s", (serialnumber,))
        if not self.cursor.fetchone():
            messagebox.showerror("Error", "No record found for the given serial number.")
            return

        serial = 0
        device_name = ""
        sap = 0

        voltage = []
        current = []
        time_in_seconds = []
        x = 0

        for row in self.cursor:
            x = x + 1
            serial = row[0]
            device_name = row[1]
            sap = row[2]
            voltage.append(row[5])
            current.append(row[6])
            time_in_seconds.append(x)

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_title("Serial: " + str(serial) + "\nName: " + str(device_name) + "\nSap: " + str(sap))
        ax.set_xlabel("Time")

        # Rysowanie linii dla danych napięcia i prądu
        l1, = ax.plot(voltage, visible=False, label='Voltage')
        l2, = ax.plot(current, visible=False, label='Current')

        # Tworzenie listy zawierającej linie reprezentujące napięcie i prąd
        lines = [l1, l2]

        rax = fig.add_axes([0.05, 0.4, 0.1, 0.15], facecolor='lightgoldenrodyellow')
        labels = []
        visibility = []
        for line in lines:
            labels.append(str(line.get_label()))
            visibility.append(line.get_visible())

        check = CheckButtons(rax, labels, visibility)

        def toggle(label):
            index = labels.index(label)
            lines[index].set_visible(not lines[index].get_visible())
            fig.canvas.draw_idle()

        check.on_clicked(toggle)
        plt.show()
