import PySimpleGUI as sg
from utils import selectScreen, lockDrive, unlockDrive


while True:
    action, values, password = selectScreen()
    if action == "lock":
        lockDrive(values, password)
    elif action == "unlock":
        returnValue = unlockDrive(values, password)
        if returnValue == "IncorrectPassword":
            sg.popup_error("Incorrect password")
    else:
        break
