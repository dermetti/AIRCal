import PyInstaller.__main__

# For Windows use 'AIRCal_icon.ico;.'
# For macOS use 'AIRCal_icon.ico:.'

PyInstaller.__main__.run([
    'class_gui.py',
    '--onefile',
    '--windowed',
    '-n AIRCal-0.9.1',
    #'--add-data', 'AIRCal_icon.ico;.',
    '-iAIRCal_icon.ico',
    '--upx-dir=C:/Users/derme/Documents/upx-4.1.0-win64'
    ])