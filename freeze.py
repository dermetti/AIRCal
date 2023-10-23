import PyInstaller.__main__

PyInstaller.__main__.run([
    'class_gui.py',
    '--onefile',
    '--windowed',
    '-n ARCal-0.9.0',
    '--upx-dir=C:/Users/derme/Documents/upx-4.1.0-win64'
    ])