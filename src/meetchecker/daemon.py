import sys
import threading
import time
import queue
from rich import console
import subprocess
import webbrowser


from meetchecker.core import run


def add_input(input_queue):
    while True:
        input_queue.put(sys.stdin.readline(1))


class Daemon:
    def __init__(self, config, interval, wsl):
        self.config = config
        self.interval = interval
        self.wsl = wsl
        self.console = console.Console()

    def create_status(self, remaining):
        commands = " ".join(
            [
                f"[blue]{cmd[0]}[/blue]{cmd[1:]}"
                for cmd in ("quit", "browser", "refresh")
            ]
        )
        return f"Refresh in [red]{remaining:.0f}[/red] seconds.  Commands: {commands}"

    def run(self):
        self.input_queue = queue.Queue()
        input_thread = threading.Thread(target=add_input, args=(self.input_queue,))
        input_thread.daemon = True
        input_thread.start()
        start = time.time()
        elapsed = 0
        with self.console.status("Meet Checker", spinner="bouncingBall") as status:
            while True:
                time.sleep(0.5)
                if not self.input_queue.empty():
                    input = self.input_queue.get().strip("\n")
                else:
                    input = None

                elapsed = time.time() - start
                if elapsed > self.interval or input == "r":
                    self.console.log("[blue]Refreshing...[/blue]")
                    run(
                        self.config["file"],
                        self.config["output"],
                        self.config["checks"],
                    )
                    start = time.time()
                    elapsed = 0
                else:
                    until_refresh = self.interval - elapsed
                    status.update(
                        self.create_status(until_refresh),
                        spinner="bouncingBall",
                    )

                if input == "q":
                    self.console.log("Quitting...")
                    break
                elif input == "b":
                    self.console.log("Opening check results in browser...")
                    self.open_in_browser()

    def open_in_browser(self):
        filepath = self.config["output"]
        filepath += "?refresh=1"
        if self.wsl:
            # adjust filepath for windows WSL
            if filepath.startswith("/mnt/c/"):
                filepath = filepath.replace("/mnt/c/", "/c:/")
            cmd = ["cmd.exe", "/C", "start", filepath]
            subprocess.run(cmd, check=False, capture_output=False)
        else:
            url = f"file://{filepath}"
            webbrowser.open(url)
