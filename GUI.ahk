#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
#SingleInstance force
; Create the ListView with two columns, Name and Size:
GUI, Add, Button, w20, Refresh
Gui, Add, ListView, r20 w700 gMyListView, Name

; Gather a list of file names from a folder and put them into the ListView:
ButtonRefresh:
if (A_GuiEvent = "Click"){
    LV_Delete()
    Loop, %A_ScriptDir%\Output\*
        LV_Add("", A_LoopFileName, 0)
}
LV_Delete()
Loop, %A_ScriptDir%\Output\*
    LV_Add("", A_LoopFileName, 0)
LV_ModifyCol()  ; Auto-size each column to fit its contents.

; Display the window and return. The script will be notified whenever the user double clicks a row.
Gui, Show
return

MyListView:
if (A_GuiEvent = "DoubleClick")
{
    LV_GetText(RowText, A_EventInfo)  ; Get the text from the row's first field.
    Run, %A_ScriptDir%\Output\%RowText%
}
return

GuiClose:  ; Indicate that the script should exit automatically when the window is closed.
ExitApp