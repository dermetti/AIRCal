import PyInstaller.__main__

PyInstaller.__main__.run([
    'class_gui.py',
    '--onefile',
    '--windowed',
    '-n AIRCal-0.9.1',
    '-iAIRCal_icon.ico',
    '--upx-dir=C:/Users/derme/Documents/upx-4.1.0-win64'
    ])