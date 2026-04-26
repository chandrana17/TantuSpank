import subprocess, sys, os

os.chdir(r"C:\CHAND\TantuSpank")
python = r"C:\CHAND\TantuSpank\venv\Scripts\python.exe"

print("=== Building TantuSpank with NUITKA (native C compilation) ===")
print("This bypasses Smart App Control by producing real native code")
print()

cmd = [
    python, "-m", "nuitka",
    "--standalone",
    "--onefile",
    "--windows-console-mode=disable",
    "--windows-icon-from-ico=icon.ico",
    "--company-name=TantuCore Studio",
    "--product-name=TantuSpank",
    "--file-version=1.0.0.0",
    "--product-version=1.0.0.0",
    "--file-description=TantuSpank - USB Prank Utility",
    "--copyright=Copyright 2026 TantuCore Studio",
    "--include-data-dir=assets=assets",
    "--include-data-dir=sound-packs=sound-packs",
    "--include-data-file=icon.ico=icon.ico",
    "--include-data-file=icon.png=icon.png",
    "--enable-plugin=tk-inter",
    "--output-filename=TantuSpank.exe",
    "--output-dir=nuitka_dist",
    "--remove-output",
    "--assume-yes-for-downloads",
    "detect.py"
]

print("Command:", " ".join(cmd[:5]), "... [truncated]")
print()

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
for line in proc.stdout:
    print(line, end='', flush=True)
proc.wait()

print(f"\nExit code: {proc.returncode}")
if proc.returncode == 0:
    exe_path = os.path.join("nuitka_dist", "TantuSpank.exe")
    if os.path.exists(exe_path):
        size = os.path.getsize(exe_path)
        print(f"=== NUITKA BUILD SUCCESS ===")
        print(f"EXE: {exe_path}")
        print(f"Size: {size / 1024 / 1024:.1f} MB")
    else:
        print("WARNING: EXE not found at expected path, checking...")
        for root, dirs, files in os.walk("nuitka_dist"):
            for f in files:
                if f.endswith(".exe"):
                    full = os.path.join(root, f)
                    print(f"  Found: {full} ({os.path.getsize(full) / 1024 / 1024:.1f} MB)")
else:
    print("=== BUILD FAILED ===")
