from colorama import init,Fore
from function_update import menu_utama,clear
import sys
import time

def loading_animation():
    chars = "/—\|"
    for char in chars:
        sys.stdout.write('\r' + 'Loading ' + char)
        sys.stdout.flush()
        time.sleep(1)

    sys.stdout.write('\r' + 'Loading complete!    \n')

# Contoh penggunaan
clear()
print(Fore.LIGHTCYAN_EX + "===========================================")
print("========= PENGELOLAAN DATA WISUDA =========")
print("===========================================" + Fore.LIGHTGREEN_EX)
loading_animation()

init()
    
menu_utama()
