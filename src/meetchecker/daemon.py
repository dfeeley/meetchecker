import threading
import time
import platform
import queue
import readchar
from rich import console
import webbrowser


from meetchecker.core import run

stopping = False


def add_input(input_queue):
    global stopping
    while True:
        input_queue.put(readchar.readkey())
        if stopping:
            break
        time.sleep(0.1)


class Daemon:
    def __init__(self, database, output, checks, interval):
        self.database = database
        self.output = output
        self.checks = checks
        self.interval = interval
        self.console = console.Console()

    def run(self):
        self.input_queue = queue.Queue()
        input_thread = threading.Thread(target=add_input, args=(self.input_queue,))
        input_thread.daemon = True
        input_thread.start()
        start = time.time()
        elapsed = 0
        run(
            self.database,
            self.output,
            self.checks,
        )
        with self.console.status("Meet Checker", spinner="aesthetic") as status:
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
                        self.database,
                        self.output,
                        self.checks,
                    )
                    start = time.time()
                    elapsed = 0
                else:
                    until_refresh = self.interval - elapsed
                    status.update(
                        self.create_status(until_refresh),
                        # spinner="aesthetic",
                    )

                if input == "q":
                    self.console.log("Quitting...")
                    global stopping
                    stopping = True
                    print("Hit q again to quit")
                    input_thread.join()
                    break
                elif input == "b":
                    self.console.log("Opening check results in browser...")
                    self.open_in_browser()

    def create_status(self, remaining):
        commands = " ".join(
            [
                f"[blue]{cmd[0]}[/blue]{cmd[1:]}"
                for cmd in ("quit", "browser", "refresh")
            ]
        )
        return f"Refresh in [red]{remaining:.0f}[/red] seconds.  Commands: {commands}"

    @property
    def wsl(self):
        return "wsl" in platform.uname().release.lower()

    def open_in_browser(self):
        filepath = self.output
        url = f"file://{filepath}?refresh=1"
        if self.wsl:
            # adjust filepath for windows WSL
            url = url.replace("/mnt/c/", "c:/")
            print(
                "Unable to open browser directly under WSL, so please copy/paste the url:"
            )
            print(url)
        else:
            webbrowser.open(url)
