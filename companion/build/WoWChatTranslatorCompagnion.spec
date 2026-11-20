# PyInstaller spec: one .exe (addon and glossary embedded), with the translation models in a
# "models" folder next to it. Inside the .exe, the models (~500 MB) would be unpacked to a
# temporary folder at every launch (several seconds). A splash screen shows up at once.
# Build from the companion folder:  pyinstaller --noconfirm build/WoWChatTranslatorCompagnion.spec

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

ROOT = Path(SPECPATH).parent          # companion/
REPO = ROOT.parent                    # repository root

datas = [
    (str(REPO / "addon" / "WoWChatTranslator"), "addon/WoWChatTranslator"),
    (str(ROOT / "data"), "data"),
]
datas += collect_data_files("py3langid")
datas += collect_data_files("certifi")

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=collect_dynamic_libs("ctranslate2"),
    datas=datas,
    hiddenimports=["PIL.ImageTk", "PIL._tkinter_finder", "pystray._win32", "mss.windows", "dxcam", "comtypes", "comtypes.stream", "truststore", "certifi"],
    excludes=["torch", "transformers", "tensorflow", "matplotlib", "pandas", "scipy", "lingua", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)

splash = Splash(
    str(ROOT / "build" / "splash.png"),
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    always_on_top=False,
)

exe = EXE(
    pyz,
    a.scripts,
    splash,
    splash.binaries,
    a.binaries,
    a.datas,
    [],
    name="WoWChatTranslatorCompagnion",
    icon=str(ROOT / "build" / "icon.ico"),
    console=False,
    upx=False,
    runtime_tmpdir=None,
)
