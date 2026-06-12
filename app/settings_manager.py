import os
import sys
import subprocess
from PySide6.QtCore import QSettings


class SettingsManager:
    def __init__(self):
        self._settings = QSettings("Clipser", "Clipser")

    def get(self, key, default=None, type=None):
        return self._settings.value(key, default, type=type)

    def set(self, key, value):
        self._settings.setValue(key, value)
        self._settings.sync()

    @property
    def auto_start(self):
        return self.get("auto_start", False, type=bool)

    @auto_start.setter
    def auto_start(self, value):
        self.set("auto_start", value)
        self._update_auto_start(value)

    @property
    def max_entries(self):
        return self.get("max_entries", 200, type=int)

    @max_entries.setter
    def max_entries(self, value):
        self.set("max_entries", value)

    @property
    def show_timestamps(self):
        return self.get("show_timestamps", True, type=bool)

    @show_timestamps.setter
    def show_timestamps(self, value):
        self.set("show_timestamps", value)

    @property
    def theme(self):
        return self.get("theme", "dark", type=str)

    @theme.setter
    def theme(self, value):
        self.set("theme", value)

    @property
    def hotkey(self):
        return self.get("hotkey", "ctrl+shift+v", type=str)

    @hotkey.setter
    def hotkey(self, value):
        self.set("hotkey", value)

    def _update_auto_start(self, enable):
        if sys.platform == "win32":
            self._toggle_windows_autostart(enable)
        else:
            self._toggle_linux_autostart(enable)

    def _toggle_windows_autostart(self, enable):
        startup_dir = os.path.join(
            os.environ.get("APPDATA", ""),
            r"Microsoft\Windows\Start Menu\Programs\Startup",
        )
        shortcut_path = os.path.join(startup_dir, "Clipser.lnk")
        if enable:
            self._create_windows_shortcut(shortcut_path)
        elif os.path.exists(shortcut_path):
            os.remove(shortcut_path)

    def _create_windows_shortcut(self, shortcut_path):
        if getattr(sys, "frozen", False):
            target = sys.executable
            arguments = ""
            workdir = os.path.dirname(sys.executable)
        else:
            target = sys.executable
            script = os.path.abspath(sys.argv[0])
            arguments = f'"{script}"'
            workdir = os.path.dirname(script)

        ps_script = (
            "$WshShell = New-Object -ComObject WScript.Shell\n"
            f"$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')\n"
            f"$Shortcut.TargetPath = '{target}'\n"
        )
        if arguments:
            ps_script += f"$Shortcut.Arguments = '{arguments}'\n"
        ps_script += (
            f"$Shortcut.WorkingDirectory = '{workdir}'\n"
            "$Shortcut.Description = 'Clipser - Lightweight Clipboard Manager'\n"
            "$Shortcut.WindowStyle = 7\n"
            "$Shortcut.Save()\n"
        )
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            creation_flags = 0
            if hasattr(subprocess, "CREATE_NO_WINDOW"):
                creation_flags = subprocess.CREATE_NO_WINDOW
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True,
                startupinfo=startupinfo,
                creationflags=creation_flags,
            )
        except Exception:
            pass

    def _toggle_linux_autostart(self, enable):
        autostart_dir = os.path.join(
            os.path.expanduser("~"), ".config", "autostart"
        )
        desktop_path = os.path.join(autostart_dir, "clipser.desktop")
        if enable:
            os.makedirs(autostart_dir, exist_ok=True)
            if getattr(sys, "frozen", False):
                exec_line = sys.executable
            else:
                exec_line = f'{sys.executable} "{os.path.abspath(sys.argv[0])}"'
            desktop = (
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name=Clipser\n"
                "Comment=Lightweight Clipboard Manager\n"
                f"Exec={exec_line}\n"
                "Hidden=false\n"
                "NoDisplay=false\n"
                "X-GNOME-Autostart-enabled=true\n"
            )
            with open(desktop_path, "w") as f:
                f.write(desktop)
        elif os.path.exists(desktop_path):
            os.remove(desktop_path)
