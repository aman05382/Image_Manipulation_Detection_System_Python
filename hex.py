# import binascii
# filename = '1.jpg'
# with open(filename, 'rb') as f:
#     content = f.read()
# print(f'{binascii.hexlify(content)}\n')

import sys
import argparse
import os.path
# This will import all the widgets
# and modules which are available in
# tkinter and ttk module
from tkinter import *
# from tkinter.ttk import *

from prettytable import PrettyTable

filename = '2.jpg'

# creates a Tk() object
master = Tk()

t=Text(master)#Inside t ext widget we would put our table

x=PrettyTable()

x.field_names = ["Bytes", "8-bit", "string"]


with open(filename, "rb") as f:
        n = 0
        b = f.read(16)

        while b:
            s1 = " ".join([f"{i:02x}" for i in b])  # hex string
            # insert extra space between groups of 8 hex values
            s1 = s1[0:23] + " " + s1[23:]

            # ascii string; chained comparison
            s2 = "".join([chr(i) if 32 <= i <= 127 else "." for i in b])

            # print(f"{n * 16:08x}  {s1:<48}  |{s2}|")
            # hex = Label(master,text= f"{n * 16:08x}  {s1:<48}  |{s2}|")
            # hex.pack()
            x.add_row([f"{n * 16:08x}",f"{s1:<48}",f"{s2}"])

            n += 1
            b = f.read(16)
        
        t.insert(INSERT,x)#Inserting table in text widget
        t.config(state=DISABLED)
        t.pack()
        # print(f"{os.path.getsize(filename):08x}")
        # function to open a new window on a button click.
        label = Label(master,text="This is the main window " f"{os.path.getsize(filename):08x}")
        label.pack(pady=10)

# mainloop, runs infinitely
mainloop()









# import sys
# import argparse
# import os.path


# parser = argparse.ArgumentParser()
# parser.add_argument(
#     "FILE", help="the name of the file that you wish to dump", type=str)
# args = parser.parse_args()

# try:
#     with open(args.FILE, "rb") as f:
#         n = 0
#         b = f.read(16)

#         while b:
#             s1 = " ".join([f"{i:02x}" for i in b])  # hex string
#             # insert extra space between groups of 8 hex values
#             s1 = s1[0:23] + " " + s1[23:]

#             # ascii string; chained comparison
#             s2 = "".join([chr(i) if 32 <= i <= 127 else "." for i in b])

#             print(f"{n * 16:08x}  {s1:<48}  |{s2}|")

#             n += 1
#             b = f.read(16)
#     print(f"{os.path.getsize(args.FILE):08x}")

# except Exception as e:
#     print(__file__, ": ", type(e).__name__, " - ", e, sep="", file=sys.stderr)