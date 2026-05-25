"""py2app build configuration for text2prompt."""

from setuptools import setup

APP = ['src/text2prompt/__main__.py']
DATA_FILES = [('resources', ['assets/text2prompt.icns'])]
OPTIONS = {
    'argv_emulation': False,
    'plist': {
        'CFBundleName': 'text2prompt',
        'CFBundleDisplayName': 'text2prompt',
        'CFBundleIdentifier': 'com.text2prompt.app',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'CFBundleIconFile': 'text2prompt.icns',
        'NSHumanReadableCopyright': 'MIT License',
        'LSUIElement': True,
        'LSMinimumSystemVersion': '26.0.0',
    },
}

setup(
    name='text2prompt',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
)
