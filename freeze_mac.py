import PyInstaller.__main__

PyInstaller.__main__.run([
    'AIRCal_gui_mac.py',
    '--onefile',
    '--windowed',
    '-n AIRCal-0.1.0-macOS',
    '-iAIRCal_icon.ico'
    ])