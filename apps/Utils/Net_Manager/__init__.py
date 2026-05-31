"""Network Manager — list IFs, toggle wlan, show IP. No shell."""
import subprocess

from PiPerW.driver.display import Display
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.utils.Menu import Menu

display = Display()
pheripherals = Pheripherals()


def _run(argv):
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=5)
        return r.stdout.strip(), r.returncode
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return f"err: {e}", 1


def _ifaces():
    out, _ = _run(["ip", "-o", "link", "show"])
    names = []
    for line in out.splitlines():
        parts = line.split(":")
        if len(parts) > 1:
            name = parts[1].strip().split("@")[0]
            if name and name != "lo":
                names.append(name)
    return names


def _ip(iface):
    out, _ = _run(["ip", "-o", "-4", "addr", "show", iface])
    for line in out.splitlines():
        toks = line.split()
        if "inet" in toks:
            return toks[toks.index("inet") + 1]
    return "none"


class App(AppInterface):
    def run(self):
        while not self.is_stopped():
            ifs = _ifaces()
            if not ifs:
                display.text("no IFs")
                self.wait_for_input()
                return
            menu = Menu(ifs + ["[exit]"])
            menu.show()
            chosen = None
            while not self.is_stopped():
                k = pheripherals.await_key()
                if k == "up":
                    menu.previous()
                elif k == "down":
                    menu.next()
                elif k == "select":
                    chosen = menu.get_selected()
                    break
                elif k in ("back", "exit"):
                    return
                menu.show()
            if chosen == "[exit]" or chosen is None:
                return
            self._iface_menu(chosen)

    def _iface_menu(self, iface):
        while not self.is_stopped():
            ip = _ip(iface)
            display.text(f"{iface}\n{ip}\n[select] toggle\n[back] menu")
            k = pheripherals.await_key()
            if k == "select":
                _run(["sudo", "ip", "link", "set", iface, "down"])
                _run(["sudo", "ip", "link", "set", iface, "up"])
                display.text(f"{iface}\ntoggled")
            elif k in ("back", "exit"):
                return
