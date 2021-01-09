#!C:\Users\Acer\PycharmProjects\hangman\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'updates==0.1.7.1','console_scripts','updates'
__requires__ = 'updates==0.1.7.1'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('updates==0.1.7.1', 'console_scripts', 'updates')()
    )
