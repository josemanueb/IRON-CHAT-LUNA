Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
DesktopPath = WshShell.SpecialFolders("Desktop")
ScriptPath = FSO.GetAbsolutePathName(".")
LinkPath = DesktopPath & "\IRON CHAT - LUNA.lnk"
Set Shortcut = WshShell.CreateShortcut(LinkPath)
Shortcut.TargetPath = ScriptPath & "\iron-chat.bat"
Shortcut.Arguments = ""
Shortcut.WorkingDirectory = ScriptPath
Shortcut.Description = "Chatbot Inteligente con LUNA - Entrenadora Personal"
If FSO.FileExists(ScriptPath & "\robot-icon.ico") Then
    Shortcut.IconLocation = ScriptPath & "\robot-icon.ico, 0"
End If
Shortcut.Save
WScript.Echo "✅ Acceso directo creado en el escritorio!"
