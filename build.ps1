./keylogenv/Scripts/Activate.ps1
rm -R -Force ./dist
pyinstaller -D --noconsole --clean  ./kl.py
rm ./kl.spec