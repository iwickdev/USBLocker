def secureErase(file, passes, securityLevel):
    import random
    import os
    import sys

    FileNameLength = 50
    charList = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-=[];,./!@#$%^&*(){}|_+<>?')

    # Check if the file exists
    if not os.path.exists(file):
        sys.exit(str(file) + " does not exist")

    # Run the amount of passes
    for i in range(0, passes):
        # Open file
        with open(file, 'r', encoding="utf8", errors='ignore') as f:
            fileData = f.read().splitlines()

        # Wipe current data in file
        with open(file, 'w') as f:
            f.write('')

        # Getdata and prepare to write to the file
        for line in fileData:
            writeString = ''
            # Get length of line and create a string with that length
            for write in range(0, len(line) * securityLevel):
                writeString += str(charList[random.randint(0, len(charList) - 1)])

            # Write string to file
            try:
                with open(file, 'a') as f:
                    f.write(str(writeString) + '\n')
            except:
                pass

    # Remove scrambled file
    os.remove(file)


def selectScreen():
    import os
    import PySimpleGUI as sg

    sg.theme("DarkBlue")
    layout = [
        [sg.Text("USB Locker v1.0", font=("Arial", 25))],
        [sg.Text("Select a drive from the list below and press 'Lock Drive'", size=(49, 1)),
         sg.Button("Refresh List", size=(13, 1))],
        [sg.Listbox(scanDrives(), size=(71, 10), key="driveList")],
        [sg.Text("Password:"), sg.InputText(size=(62, 1), key="passwordInput")],
        [sg.Button("Lock Drive", size=(27, 1)), sg.Button("Unlock Drive", size=(27, 1)), sg.Button("Cancel")]
    ]
    window = sg.Window("USB Locker - Select a USB to lock", layout=layout)
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "Cancel":
            return "Exit", None, None

        if event == "Refresh List":
            window["driveList"].Update(scanDrives())

        if event == "Lock Drive":
            if not values["driveList"]:
                sg.popup_error("You must select a drive to lock")
            elif not values["passwordInput"]:
                sg.popup_error("You must put in a password")
            elif os.path.exists(values["driveList"][0] + "usblock.usbpass"):
                sg.popup_error("This drive is already locked")
            else:
                window.close()
                return "lock", values["driveList"][0], values["passwordInput"]

        if event == "Unlock Drive":
            if not values["driveList"]:
                sg.popup_error("You must select a drive to unlock")
            elif not values["passwordInput"]:
                sg.popup_error("You must put in a password")
            elif not os.path.exists(values["driveList"][0] + "usblock.usbpass"):
                sg.popup_error("This drive is not locked")
            else:
                window.close()
                return "unlock", values["driveList"][0], values["passwordInput"]


def scanDrives():
    import os
    drives = []
    for div in list("ABDEFGHIJKLMNOPQRSTUVWSYZ"):
        if os.path.exists(f"{div}:/"):
            drives.append(f"{div}:/")
    return drives


def dirAllFP(path):
    import os
    filesList = []
    for dirpath, subdirs, files in os.walk(path):
        for x in files:
            filesList.append(os.path.join(dirpath, x))
    return filesList


def lockDrive(drive, password):
    import hashlib
    import pyAesCrypt
    import PySimpleGUI as sg

    indexDrive = dirAllFP(drive)

    sg.theme("DarkBlue")
    layout = [
        [sg.Text("Locking Drive: " + drive, font=("Arial", 20))],
        [sg.ProgressBar(len(indexDrive), orientation="h", size=(50, 20), key="progressBar")]
    ]
    window = sg.Window("Locking drive", layout=layout)

    fileLocateion = 0
    for file in indexDrive:
        fileName = file + ".usblock"
        try:
            pyAesCrypt.encryptFile(file, fileName, password, 64 * 1024)
            secureErase(file, 2, 2)
        except:
            pass

        event, values = window.read(timeout=0)
        if event == sg.WINDOW_CLOSED:
            window.close()
        window["progressBar"].update_bar(fileLocateion)

        fileLocateion += 1

    with open(drive + "usblock.usbpass", "w") as f:
        f.write(hashlib.sha256(password.encode("utf-8")).hexdigest())

    window.close()


def unlockDrive(drive, password):
    import os
    import hashlib
    import pyAesCrypt
    import PySimpleGUI as sg

    indexDrive = dirAllFP(drive)

    sg.theme("DarkBlue")
    layout = [
        [sg.Text("Unlocking Drive: " + drive, font=("Arial", 20))],
        [sg.ProgressBar(len(indexDrive), orientation="h", size=(50, 20), key="progressBar")]
    ]
    window = sg.Window("Unlocking drive", layout=layout)

    with open(drive + "usblock.usbpass") as f:
        if not hashlib.sha256(password.encode("utf-8")).hexdigest() == f.read():
            return "IncorrectPassword"

    fileLocation = 0
    for file in indexDrive:
        fileName = file.replace(".usblock", "")
        try:
            pyAesCrypt.decryptFile(file, fileName, password, 64 * 1024)
            os.remove(file)
        except:
            pass

        event, values = window.read(timeout=0)
        if event == sg.WINDOW_CLOSED:
            window.close()
        window["progressBar"].update_bar(fileLocation)

        fileLocation += 1

    os.remove(drive + "usblock.usbpass")

    window.close()
