from tkinter import *
import tkinter as tk
from tkinter import PhotoImage, Toplevel, ttk, filedialog
import numpy
import pandas as pd
import link_budget_func
from random import randrange
import random
from link_budget_func import calc_power_single_point
from link_budget_func import calc_link_budget
from link_budget_func import map_to_earth


#window formation
window = tk.Tk()
window.title("Earth Remote Sensing")
window.configure(bg = 'black')
#window geometry and formatting
window_width = 600
window_height = 400 
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)
window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
image1 = PhotoImage(file = r"C:\Users\tanis\OneDrive\Desktop\Fall 22\VIP_ERS\VIP_ERS\earth.png")
xyz = tk.Label(window, image = image1)
xyz.place(x=25, y=55)
greeting = tk.Label(text="Welcome to ERS", font = ("Eurostile Bold", 30), bg = "black", fg = 'white')
greeting.pack()

#for user entered parameters
def create():
    win = Toplevel(window)
    win.title("Location explorer")
    window_width = 600
    window_height = 400 
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    center_x = int(screen_width/2 - window_width / 2)
    center_y = int(screen_height/2 - window_height / 2)
    win.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    ttk.Label(win, text="Latitude").grid(row=0)
    ttk.Label(win, text="Longitude").grid(row=1)
    ttk.Label(win, text="Minimum Frequency").grid(row=2)
    ttk.Label(win, text="Maximum Frequency").grid(row=3)
    ttk.Label(win, text="Power Threshold").grid(row=4)
    lat = ttk.Entry(win)
    long = ttk.Entry(win)
    min_freq = ttk.Entry(win)
    max_freq = ttk.Entry(win)
    power_thresh = ttk.Entry(win)

    lat.grid(row=0, column=1)
    long.grid(row=1, column=1)
    min_freq.grid(row=2, column=1)
    max_freq.grid(row=3, column=1)
    power_thresh.grid(row = 4, column = 1)
    def show_entry_fields():
        print("Latitude: %s\nLongitude: %s\nMinimum Frequency: %s\nMaximum Frequency: %s\nPower Threshold: %s\n" % (lat.get(), long.get(), min_freq.get(), max_freq.get(), power_thresh.get()))
        print(lat.get())
        print("ffff")
        print(type(lat))
        df = sat_list(float(lat.get()), float(long.get()), float(max_freq.get()), float(min_freq.get()), float(power_thresh.get()) * 10**-9)
        print(df)

    def exit():
        window.destroy()

    ttk.Button(win, text = "Exit", command = exit).grid(row=5, column=1, sticky=tk.W, pady=4)
    ttk.Button(win, text='Enter', command=show_entry_fields).grid(row=5, column=1, sticky=tk.W, pady=4)

    

    #df = sat_list(float(lat.get()), float(long.get()), float(max_freq.get()), float(min_freq.get()), float(power_thresh.get() * 10**-9))
    #print(df)


#database input and viewing
def display_database():
    win = Toplevel(window)
    win.title("Database Viewer")
    window_width = 600
    window_height = 400 
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    center_x = int(screen_width/2 - window_width / 2)
    center_y = int(screen_height/2 - window_height / 2)
    win.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    frame1 = tk.LabelFrame(win, text = "Satellite Data")
    frame1.place(height = 250, width = 500)

    file_frame = ttk.LabelFrame(win, text = "Open File")
    file_frame.place(height=100, width=400, rely=0.65, relx=0)
    button1 = ttk.Button(file_frame, text="Browse A File", command=lambda: File_dialog())
    button1.place(rely=0.65, relx=0.50)
    #button2 = ttk.Button(file_frame, text="Load File", command=lambda: Load_excel_data())
    #button2.place(rely=0.65, relx=0.20)
    # The file/file path text
    label_file = ttk.Label(file_frame, text="No File Selected")
    label_file.place(rely=0, relx=0)
    tv1 = ttk.Treeview(frame1)
    tv1.place(relheight=1, relwidth=1) # set the height and width of the widget to 100% of its container (frame1).
    treescrolly = ttk.Scrollbar(frame1, orient="vertical", command=tv1.yview) # command means update the yaxis view of the widget
    treescrollx = ttk.Scrollbar(frame1, orient="horizontal", command=tv1.xview) # command means update the xaxis view of the widget
    tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set) # assign the scrollbars to the Treeview Widget
    treescrollx.pack(side="bottom", fill="x") # make the scrollbar fill the x axis of the Treeview widget
    treescrolly.pack(side="right", fill="y") # make the scrollbar fill the y axis of the Treeview widget

    def File_dialog():
        """This Function will open the file explorer and assign the chosen file path to label_file"""
        filename = filedialog.askopenfilename(initialdir="/", title="Select A File", filetype=(("All Files", "*.*"), ("xlsx files", "*.xlsx")))
        label_file["text"] = filename
        file_path = label_file["text"]
        try:
            excel_filename = r"{}".format(file_path)
            if excel_filename[-4:] == ".csv":
                df = pd.read_csv(excel_filename)
            else:
                df = pd.read_excel(excel_filename)

        except ValueError:
            ttk.messagebox.showerror("Information", "The file you have chosen is invalid")
            return None
        except FileNotFoundError:
            ttk.messagebox.showerror("Information", f"No such file as {file_path}")
            return None
        
        clear_data()
        tv1["column"] = list(df.columns)
        tv1["show"] = "headings"
        for column in tv1["columns"]:
            tv1.heading(column, text=column) # let the column heading = column name

        df_rows = df.to_numpy().tolist() # turns the dataframe into a list of lists
        for row in df_rows:
            tv1.insert("", "end", values=row) # inserts each list into the treeview. For parameters see https://docs.python.org/3/library/tkinter.ttk.html#tkinter.ttk.Treeview.insert
        data = df
        return(df)
    return(data)    
    '''def Load_excel_data():
        """If the file selected is valid this will load the file into the Treeview"""
        file_path = label_file["text"]
        try:
            excel_filename = r"{}".format(file_path)
            if excel_filename[-4:] == ".csv":
                df = pd.read_csv(excel_filename)
            else:
                df = pd.read_excel(excel_filename)

        except ValueError:
            ttk.messagebox.showerror("Information", "The file you have chosen is invalid")
            return None
        except FileNotFoundError:
            ttk.messagebox.showerror("Information", f"No such file as {file_path}")
            return None
        
        clear_data()
        tv1["column"] = list(df.columns)
        tv1["show"] = "headings"
        for column in tv1["columns"]:
            tv1.heading(column, text=column) # let the column heading = column name

        df_rows = df.to_numpy().tolist() # turns the dataframe into a list of lists
        for row in df_rows:
            tv1.insert("", "end", values=row) # inserts each list into the treeview. For parameters see https://docs.python.org/3/library/tkinter.ttk.html#tkinter.ttk.Treeview.insert
        return None'''

    def clear_data():
        tv1.delete(*tv1.get_children())
        return None

#universal exit button
def exit():
    window.destroy()


def sat_list(TargetLon, TargetLat, MaxFreq, MinFreq, power_threshold, df):
    #calculations
    MaxLon = TargetLon + 81.4  #degrees
    MinLon = TargetLon - 81.4  #degrees

    # account for east and west scale
    if MaxLon > 180:
        MaxLon = MaxLon - 360
    if MinLon <= -180:
        MinLon = MinLon + 360
    #need to error check or clean values in any way? like null values

    '''Sort database'''
    # double check this works with all possible lon values.
    df = df[(df.Longitude <= MaxLon) & (df.Longitude >= MinLon)]
    df = df[(df.Frequency <= MaxFreq) & (df.Frequency >= MinFreq)]

    outputs = []


    for i in range(0,len(df)):
        temp = calc_power_single_point(TargetLon, TargetLat, df['Longitude'].iloc[i], 0, 20, [df['Beam theta'].iloc[i], df['Beam Phi'].iloc[i]])
        outputs.append(temp)
    outputs.sort(reverse=True)
    df.insert(5, 'Power', outputs, True)
    df = df[(df.Power > power_threshold)]

    return(df)



sat_lat_database = []
sat_long_database = []
for i in range(0,4200):
    sat_lat_database.append(randrange(0,80))
    sat_long_database.append(randrange(0,80))
pep_max = 20
beams = []
for i in range(0, 4200):
    beams.append([randrange(0, 8), randrange(0, 8)])


randlat = random.randrange(len(sat_lat_database))
sat_lat = sat_lat_database[randlat]
randlong = random.randrange(len(sat_long_database))
sat_long = sat_long_database[randlong]
randbeam = random.randrange(len(beams))
beam_angles = beams[randbeam]

#calc_link_budget(sat_lat, sat_long, pep_max, beams)

s = ttk.Style()
s.configure('.', font=('Cascadia Code', 13))
database = ttk.Button(window, text = "Satellite Database", command = display_database).pack(ipadx = 2, ipady=5, pady=8)
location = ttk.Button(window, text = "Enter Location", command = create).pack(ipadx = 2, ipady=5, pady = 9)
linkbud = ttk.Button(window, text = "Link Budget", command = calc_link_budget).pack(ipadx = 2, ipady = 5, pady = 11)

exit = ttk.Button(window, text = "Exit", command = exit).pack(ipadx = 2, ipady=5, pady = 9.5)
window.mainloop()