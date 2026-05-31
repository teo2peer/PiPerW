"""File Browser — navigate public/, view text, delete with confirm."""
import os

from PiPerW.driver.display import Display
from PiPerW.driver.pheripherals import Pheripherals
from PiPerW.interfaces.app_interface import AppInterface
from PiPerW.utils.Menu import Menu

display = Display()
pheripherals = Pheripherals()


class App(AppInterface):
    def run(self):
        root = self.get_public_dir()
        self._browse(root)

    def _browse(self, path):
        while not self.is_stopped():
            try:
                entries = sorted(os.listdir(path))
            except OSError as e:
                display.text(f"err: {e}")
                self.wait_for_input()
                return
            options = [".."] + entries + ["[exit]"]
            menu = Menu(options)
            menu.show()
            while not self.is_stopped():
                k = pheripherals.await_key()
                if k == "up":
                    menu.previous()
                elif k == "down":
                    menu.next()
                elif k == "select":
                    sel = menu.get_selected()
                    if sel == "[exit]":
                        return
                    if sel == "..":
                        parent = os.path.dirname(path.rstrip(os.sep))
                        if parent:
                            path = parent
                        break
                    target = os.path.join(path, sel)
                    if os.path.isdir(target):
                        path = target
                        break
                    self._file_action(target)
                    break
                elif k in ("back", "exit"):
                    return
                menu.show()

    def _file_action(self, path):
        menu = Menu(["View", "Delete", "Back"])
        while not self.is_stopped():
            menu.show()
            k = pheripherals.await_key()
            if k == "up":
                menu.previous()
            elif k == "down":
                menu.next()
            elif k == "select":
                sel = menu.get_selected()
                if sel == "Back":
                    return
                if sel == "View":
                    try:
                        with open(path, "rb") as f:
                            data = f.read(400)
                        display.text(data.decode("utf-8", "replace"))
                    except OSError as e:
                        display.text(f"err: {e}")
                    self.wait_for_input()
                    return
                if sel == "Delete":
                    confirm = Menu(["No", "Yes"])
                    confirm.show()
                    while not self.is_stopped():
                        ck = pheripherals.await_key()
                        if ck == "up":
                            confirm.previous()
                        elif ck == "down":
                            confirm.next()
                        elif ck == "select":
                            if confirm.get_selected() == "Yes":
                                try:
                                    os.remove(path)
                                    display.text("Deleted")
                                except OSError as e:
                                    display.text(f"err: {e}")
                                self.wait_for_input()
                            return
                        elif ck in ("back", "exit"):
                            return
                        confirm.show()
            elif k in ("back", "exit"):
                return
