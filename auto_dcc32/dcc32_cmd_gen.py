import subprocess
from pathlib import Path

dcc32   = Path("C:\\Program Files (x86)\\Borland\\Delphi7\\Bin\\DCC32.EXE")
project = Path("C:\\DW\\Practice\\practice.dpr")

# file = open(str(cmds), "wt")
# file.write(r'-I"c:\program files (x86)\embarcadero\studio\17.0\lib\Win32\debug"')
# file.close()

proc = subprocess.Popen(
    args="cd " + str(project.parent),
    shell=True
)

cmds    = ""
for i in range(3):
    proc_dcc32 = subprocess.Popen(
        args=f'"{str(dcc32)}" {cmds} {str(project)}', 
        shell=True,
        stdout=subprocess.PIPE
    )
    out, err = proc_dcc32.communicate()

    if 'Fatal: File not found: ' in out.decode("utf-8"):
        file = 

    print(out.decode("utf-8"))