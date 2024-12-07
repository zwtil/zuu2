

from time import sleep

from src.zuu.common.timelyKill import timelyKill


@timelyKill()
def test():
    from zuu.pkg.subprocess import execute 
    execute("notepad.exe")
    execute("notepad.exe")
    execute("notepad.exe")
    execute("notepad.exe")
    sleep(5)

