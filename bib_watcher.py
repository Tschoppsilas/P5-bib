import subprocess, time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

REPO = Path(r"C:\Users\silas\OneDrive\FHNW\07_Semester\P5\P5-bib")   # <-- anpassen
BIB = "references.bib"

def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)

class Handler(FileSystemEventHandler):
    last = 0
    def on_any_event(self, event):
        paths = [event.src_path, getattr(event, "dest_path", "") or ""]
        if not any(str(p).endswith(BIB) for p in paths):
            return
        if time.time() - self.last < 5:      # Mehrfach-Events abfangen
            return
        self.last = time.time()
        time.sleep(2)                        # Zotero fertig schreiben lassen
        git("add", BIB)
        if git("diff", "--cached", "--quiet").returncode == 0:
            return                           # nichts geändert
        git("commit", "-m", "auto: update bib")
        git("pull", "--rebase")
        result = git("push")
        print(time.strftime("%H:%M:%S"), "gepusht" if result.returncode == 0 else result.stderr)

observer = Observer()
observer.schedule(Handler(), str(REPO), recursive=False)
observer.start()
print("Überwache", REPO / BIB)
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()