# VIP_ERS
The following files are necessary for the code to work: 
ngso1.py
ngso2.py
s672.py
sirion.py
gensatlist.py
link_budget_func.py
linkbudget.py
APSND_499V01.py
sort.py
program.py
 
Program.py is the file required to run the program.

Signals of Opportunity (SoOp) is a bistatic method of remote sensing using existing signals. Satellites, especially transmitters in geostationary orbit (GEO) are promising sources of SoOp. The main goal of this project is to provide a new way of aggregating and visualizing these signals to find suitable candidates for SoOp research. Previously, a version of the  program was created in Python to calculate and visualize radiated power of GEO satellites onto the surface of the earth based on the user input. In order to investigate SoOp on a large scale, a simpler way of extracting these parameters from the database is needed. 
To solve this problem, the researchers created an application building upon the previous Python program. The user first provides a database file from the International Telecommunications Union (ITU) containing satellite parameters such as location, gain pattern, power, etc. The program generates a list of satellites that meet the power threshold then generates power density maps based on selections from the list. A graphical user interface made with the Python package Tkinter allows for intuitive and efficient navigation of the database. This streamlines the searching process for available signal sources for use in SoOp research.
