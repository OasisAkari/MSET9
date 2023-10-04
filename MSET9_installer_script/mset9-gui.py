import binascii
import os
import platform as pl
import shutil
import sys
import tkinter as tk
import tkinter.messagebox as mb
import tkinter.ttk as ttk
import traceback

VERSION = "v2beta"

p = pl.system()
if p == 'Windows':  # 0-win, 1-lin, 2-mac, x-win   lol go with the market leader i guess
    OPSYS = 0
elif p == 'Linux':
    OPSYS = 1
elif p == 'Darwin':
    OPSYS = 2
else:
    OPSYS = 0

cwd = os.path.dirname(sys.argv[0])
try:
    os.chdir(cwd)
except Exception:
    print("Failed to set cwd: " + cwd)
    exit(1)

trigger = "002F003A.txt"  # all 3ds ":/"

# old3ds 11.8-11.17
# id1_haxstr="FFFFFFFA119907488546696508A10122054B984768465946FFAA171C4346034CA047B84700900A0871A0050899CE0408730064006D00630000900A0862003900"
id1_haxstr = "FFFFFFFA119907488546696508A10122054B984768465946C0AA171C4346034CA047B84700900A0871A0050899CE0408730064006D00630000900A0862003900"

haxid1 = bytes.fromhex(id1_haxstr)  # ID1 - arm injected payload in readable format
haxid1 = haxid1.decode("utf-16le")
haxid1_path = ""
id1 = ""
id1_root = ""
id1_path = ""

ext_root = ""
oldtag = "_oldid1"
mode = 0  # 0 setup state, 1 hax state
id0_count = 0

home_menu = [0x8f, 0x98, 0x82, 0xA1, 0xA9, 0xB1]  # us,eu,jp,ch,kr,tw
mii_maker = [0x217, 0x227, 0x207, 0x267, 0x277, 0x287]  # us,eu,jp,ch,kr,tw


class Mset9GUI(ttk.Frame):

    def __init__(self, parent: tk.Tk = None):
        super().__init__(parent)

        self.rowconfigure(0, weight=0)
        self.columnconfigure(0, weight=1)

        control_frame = ttk.Frame(self)
        control_frame.grid(row=0, column=0)

        setup_mset9 = ttk.Button(control_frame, text='Setup MSET9', command=self.setup)
        setup_mset9.grid(row=0, column=0)

        inject_files = ttk.Button(control_frame, text='Inject trigger file', command=self.inject)
        inject_files.grid(row=0, column=1)

        delete_files = ttk.Button(control_frame, text='Delete trigger file', command=self.delete)
        delete_files.grid(row=1, column=0)

        remove_mset9 = ttk.Button(control_frame, text='Remove MSET9', command=self.remove)
        remove_mset9.grid(row=1, column=1)

    def setup(self):
        global mode, id1_path, id1_root, id1
        menu_ok = 0
        mii_ok = 0
        if mode:
            mb.showerror("Error", "Already setup!")
            return
        try:
            if not os.path.exists(id1_path + "/dbs/title.db"):
                mb.showinfo("Info",
                            "title.db was not found, create empty files. Reinsert SD into 3DS and go to Data Management to recreate database first.")
                os.makedirs(id1_path + "/dbs", exist_ok=True)
                with open(id1_path + "/dbs/title.db", "wb") as f:
                    f.close()
                with open(id1_path + "/dbs/import.db", "wb") as f:
                    f.close()
                sys.exit(0)
            elif not os.path.exists(id1_path + "/dbs/import.db"):
                mb.showinfo("Info",
                            "import.db was not found, create empty files. Reinsert SD into 3DS and go to Data Management to recreate database first.")
                os.makedirs(id1_path + "/dbs", exist_ok=True)
                with open(id1_path + "/dbs/title.db", "wb") as f:
                    f.close()
                with open(id1_path + "/dbs/import.db", "wb") as f:
                    f.close()
                sys.exit(0)
            check(id1_path + "/dbs/title.db", 0x31e400, 0)
            check(id1_path + "/dbs/import.db", 0x31e400, 0)
            if os.path.exists(id1_path + "/extdata/" + trigger):
                os.remove(id1_path + "/extdata/" + trigger)
            if not os.path.exists(id1_root + "/" + haxid1):
                haxid1_path = id1_root + "/" + haxid1
                os.mkdir(haxid1_path)
                os.mkdir(haxid1_path + "/extdata")
                os.mkdir(haxid1_path + "/extdata/00000000")
            if not os.path.exists(haxid1_path + "/dbs"):
                shutil.copytree(id1_path + "/dbs", haxid1_path + "/dbs")

            ext_root = id1_path + "/extdata/00000000"

            for i in home_menu:
                temp = ext_root + "/%08X" % i
                if os.path.exists(temp):
                    # print(temp,haxid1_path+"/extdata/00000000/%08X" % i)
                    shutil.copytree(temp, haxid1_path + "/extdata/00000000/%08X" % i)
                    menu_ok += 1
            assert (menu_ok == 1)
            for i in mii_maker:
                temp = ext_root + "/%08X" % i
                if os.path.exists(temp):
                    shutil.copytree(temp, haxid1_path + "/extdata/00000000/%08X" % i)
                    mii_ok += 1
            assert (mii_ok == 1)

            if os.path.exists(id1_path):
                os.rename(id1_path, id1_path + oldtag)
            id1 += oldtag
            id1_path = id1_root + "/" + id1
            mode = 1
            mb.showinfo('Info', 'Done.')
            sys.exit(0)
        except Exception:
            mb.showerror("Error", "Failed.\n" + traceback.format_exc())

    def inject(self):
        if mode == 0:
            mb.showerror("Error", "Run setup first!")
            return
        try:
            trigger_path = id1_root + "/" + haxid1 + "/extdata/" + trigger
            if not os.path.exists(trigger_path):
                with open(trigger_path, "w") as f:
                    f.write("plz be haxxed mister arm9, thx")
                    f.close()
            mb.showinfo('Info', 'Done.')
            sys.exit(0)
        except Exception:
            mb.showerror("Error", "Failed.\n" + traceback.format_exc())

    def delete(self):
        if mode == 0:
            mb.showerror("Error", "Run setup first!")
            return
        try:
            trigger_path = id1_root + "/" + haxid1 + "/extdata/" + trigger
            if os.path.exists(trigger_path):
                os.remove(trigger_path)
            mb.showinfo('Info', 'Done.')
            sys.exit(0)
        except Exception:
            mb.showerror("Failed", "Failed.\n" + traceback.format_exc())

    def remove(self):
        global mode, id1_path, id1_root, id1
        if not os.path.exists(id1_root + "/" + haxid1) and (os.path.exists(id1_path) and oldtag not in id1_path):
            mb.showinfo('Info', 'Nothing to remove!')
            return
        try:
            if os.path.exists(id1_path) and oldtag in id1_path:
                os.rename(id1_path, id1_root + "/" + id1[:32])
            # print(id1_path, id1_root+"/"+id1[:32])
            if os.path.exists(id1_root + "/" + haxid1):
                shutil.rmtree(id1_root + "/" + haxid1)
            id1 = id1[:32]
            id1_path = id1_root + "/" + id1
            mode = 0
            mb.showinfo('Info', 'Done.')
            sys.exit(0)
        except Exception:
            mb.showerror("Error", "Failed.\n" + traceback.format_exc())

        
window = tk.Tk()
window.title(f'MSET9')
screenwidth = window.winfo_screenwidth()
screenheight = window.winfo_screenheight()
width = 300
height = 60
size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
window.geometry(size)
frame = Mset9GUI(window)
frame.pack(fill=tk.BOTH, expand=True)
if not os.path.exists("Nintendo 3DS/"):
    mb.showerror("Error", "Are you sure you're running this script from the root of your SD card (right next to 'Nintendo 3DS')? You need to! \n"
                               "Current dir: %s" % cwd)
    sys.exit(0)

for root, dirs, files in os.walk("Nintendo 3DS/", topdown=True):
    for name in files:
        pass
    for name in dirs:
        if haxid1 not in name and len(name[:32]) == 32:
            try:
                temp = int(name[:32], 16)
            except:
                continue
            if type(temp) is int:
                if os.path.exists(os.path.join(root, name) + "/extdata"):
                    id1 = name
                    id1_root = root
                    id1_path = os.path.join(root, name)
                    if oldtag in name:
                        mode = 1
                else:
                    id0_count += 1


def check(keyfile, size, crc32):
    if not os.path.exists(keyfile):
        mb.showerror("Error", "%s \ndoes not exist on SD card!" % keyfile)
        sys.exit(0)
    elif size:
        s = os.path.getsize(keyfile)
        if size != s:
            mb.showerror("Error", "%s \nis size %08X, not expected %08X" % (keyfile, s, size))
            sys.exit(0)
    elif crc32:
        with open(keyfile, "rb") as f:
            temp = f.read()
        c = binascii.crc32(temp)
        if crc32 != c:
            mb.showerror("Error", "%s \n was not recognized as the correct file" % keyfile)
            sys.exit(0)


check("boot9strap/boot9strap.firm", 0, 0x08129c1f)
# check("Nintendo 3DS/Private/00020400/phtcache.bin", 0x7f53c, 0)
check("boot.firm", 0, 0)
check("boot.3dsx", 0, 0)
check("b9", 0, 0)
if id0_count == 0:
    mb.showerror("Error", "You're supposed to be running this on the 3DS SD card!\nNOT %s" % cwd)
    sys.exit(0)
assert (id0_count == 1)

if OPSYS == 0:  # windows
    _ = os.system('cls')
else:  # linux or mac
    _ = os.system('clear')

window.mainloop()
