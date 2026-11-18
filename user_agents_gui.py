import sys
import os
import time
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ua_generator
from datetime import datetime
from ua_generator.options import Options

APP_VERSION = "1.4"


class UAGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AgentX: Advanced User-Agent Generator with GUI")
        self.root.geometry("500x440")
        self.root.resizable(False, False)
        self.setup_icon()

        self.device_var = tk.StringVar(value='desktop')
        self.platform_vars = {
            'windows': tk.BooleanVar(value=True),
            'macos': tk.BooleanVar(),
            'linux': tk.BooleanVar(),
            'ios': tk.BooleanVar(),
            'android': tk.BooleanVar()
        }
        self.browser_vars = {
            'chrome': tk.BooleanVar(value=True),
            'edge': tk.BooleanVar(),
            'firefox': tk.BooleanVar(),
            'safari': tk.BooleanVar()
        }
        self.client_hints_var = tk.BooleanVar(value=False)
        self.weighted_versions_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Ready")
        self.is_random = False

        # İşçi thread'i ve iptal bayrağı
        self.worker = None
        self.stop_event = threading.Event()
        # İşçi thread arayüze doğrudan dokunmaz; mesajları bu kuyruğa bırakır
        self.ui_queue = queue.Queue()

        self.create_widgets()
        self.update_platform_options()
        self.device_var.trace_add('write', self.on_device_change)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(100, self._poll_queue)

    def setup_icon(self):
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, 'ua.ico')
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print("Icon error:", e)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        device_frame = ttk.LabelFrame(main_frame, text="Device Type")
        device_frame.pack(fill=tk.X, pady=5, anchor='w')

        ttk.Radiobutton(device_frame, text="Desktop", variable=self.device_var,
                        value='desktop', command=self.on_device_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(device_frame, text="Mobile", variable=self.device_var,
                        value='mobile', command=self.on_device_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(device_frame, text="Random", variable=self.device_var,
                        value='random', command=self.on_device_change).pack(side=tk.LEFT)

        platform_frame = ttk.LabelFrame(main_frame, text="Operating System")
        platform_frame.pack(fill=tk.X, pady=5, anchor='w')
        self.platform_container = ttk.Frame(platform_frame)
        self.platform_container.pack(side=tk.LEFT)

        browser_frame = ttk.LabelFrame(main_frame, text="Supported Browsers")
        browser_frame.pack(fill=tk.X, pady=5)

        browsers = ['chrome', 'edge', 'firefox', 'safari']
        for browser in browsers:
            ttk.Checkbutton(browser_frame, variable=self.browser_vars[browser],
                            text=browser.capitalize()).pack(side=tk.LEFT, padx=10)

        client_hints_frame = ttk.Frame(main_frame)
        client_hints_frame.pack(fill=tk.X, pady=5)
        ttk.Checkbutton(client_hints_frame, variable=self.client_hints_var,
                        text="Include Client Hints (Sec-CH-UA fields)").pack(side=tk.LEFT, padx=10)
        weighted_frame = ttk.Frame(main_frame)
        weighted_frame.pack(fill=tk.X, pady=5)
        ttk.Checkbutton(weighted_frame, variable=self.weighted_versions_var,
                        text="Use Weighted Versions (realistic distribution)").pack(side=tk.LEFT, padx=10)

        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)
        ttk.Label(file_frame, text="Count:").pack(side=tk.LEFT)
        self.count_var = tk.IntVar(value=1000)
        ttk.Spinbox(file_frame, from_=1, to=100000, textvariable=self.count_var,
                    width=8).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Save Location", command=self.choose_file).pack(side=tk.RIGHT)
        self.filepath_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.filepath_var, width=40).pack(side=tk.RIGHT,
                                                                           fill=tk.X,
                                                                           expand=True,
                                                                           padx=5)

        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(main_frame, variable=self.progress_var,
                        maximum=100).pack(fill=tk.X, pady=10)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=5)
        self.generate_button = ttk.Button(button_frame, text="Generate User Agents",
                                          command=self.start_generation)
        self.generate_button.pack(side=tk.LEFT, padx=5)
        self.cancel_button = ttk.Button(button_frame, text="Cancel",
                                        command=self.cancel_generation, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        ttk.Label(main_frame, textvariable=self.status_var).pack(fill=tk.X, pady=2)

        footer = ttk.Frame(main_frame)
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        ttk.Label(footer, text="WebAdHere Technologies", font=('Tahoma', 8)).pack(side=tk.LEFT)
        ttk.Label(footer, text="AgentX v%s" % APP_VERSION, font=('Tahoma', 8)).pack(side=tk.RIGHT)

    def update_platform_options(self):
        for widget in self.platform_container.winfo_children():
            widget.destroy()

        device_type = self.device_var.get()

        if device_type == 'random':
            self.is_random = True
            platforms = ['windows', 'macos', 'linux', 'ios', 'android']
            for platform in platforms:
                var = self.platform_vars[platform]
                var.set(True)
                text = "iOS" if platform == 'ios' else platform.capitalize()
                cb = ttk.Checkbutton(self.platform_container,
                                     text=text,
                                     variable=var,
                                     state='disabled')
                cb.pack(side=tk.LEFT, padx=5)

            for browser, var in self.browser_vars.items():
                var.set(True)
        else:
            self.is_random = False
            platforms = ['windows', 'macos', 'linux'] if device_type == 'desktop' else ['ios', 'android']

            other_platforms = ['ios', 'android'] if device_type == 'desktop' else ['windows', 'macos', 'linux']
            for platform in other_platforms:
                self.platform_vars[platform].set(False)

            for platform in platforms:
                var = self.platform_vars[platform]
                text = "iOS" if platform == 'ios' else platform.capitalize()
                ttk.Checkbutton(self.platform_container,
                                text=text,
                                variable=var).pack(side=tk.LEFT, padx=5)

            # Cihaz tipi değişince hiçbir platform seçili kalmasın diye varsayılan seç
            if not any(self.platform_vars[p].get() for p in platforms):
                default_platform = 'windows' if device_type == 'desktop' else 'android'
                self.platform_vars[default_platform].set(True)

    def choose_file(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialdir=os.path.join(os.path.expanduser('~'), 'Desktop'),
            filetypes=[("Text files", "*.txt")]
        )
        if path:
            self.filepath_var.set(path)

    def start_generation(self):
        # Önceki iş hâlâ sürüyorsa ikinci bir thread açma
        if self.worker is not None and self.worker.is_alive():
            return

        # Tüm tkinter değerlerini ana thread'de oku (işçi thread tkinter'a dokunmasın)
        try:
            count = self.count_var.get()
        except (tk.TclError, ValueError):
            messagebox.showerror("Error", "Please enter a valid number for count!")
            return

        if count < 1:
            messagebox.showerror("Error", "Count must be at least 1!")
            return

        platforms = tuple(p for p, var in self.platform_vars.items() if var.get())
        browsers = tuple(b for b, var in self.browser_vars.items() if var.get())

        if not platforms:
            messagebox.showerror("Error", "Please select at least one platform!")
            return

        if not browsers:
            messagebox.showerror("Error", "Please select at least one browser!")
            return

        filepath = self.filepath_var.get() or os.path.join(
            os.path.expanduser('~'), 'Desktop',
            'UserAgents_%s.txt' % datetime.now().strftime("%Y%m%d_%H%M%S")
        )

        device_type = None if self.device_var.get() == 'random' else self.device_var.get()

        config = {
            'count': count,
            'filepath': filepath,
            'device': device_type,
            'platforms': platforms,
            'browsers': browsers,
            'client_hints': self.client_hints_var.get(),
            'weighted': self.weighted_versions_var.get(),
        }

        self.stop_event.clear()
        self.progress_var.set(0)
        self.status_var.set("Generating %d User-Agents..." % count)
        self.generate_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)

        self.worker = threading.Thread(target=self.generate_agents, args=(config,), daemon=True)
        self.worker.start()

    def generate_agents(self, config):
        """İşçi thread: yalnızca üretim yapar, arayüzü root.after ile günceller."""
        count = config['count']
        filepath = config['filepath']
        written = 0
        started = time.time()

        try:
            options = Options() if config['weighted'] else None
            if options:
                options.weighted_versions = True

            last_update = 0.0
            with open(filepath, 'w', encoding='utf-8') as f:
                for i in range(count):
                    if self.stop_event.is_set():
                        break

                    ua = ua_generator.generate(
                        device=config['device'],
                        platform=config['platforms'],
                        browser=config['browsers'],
                        options=options
                    )

                    if config['client_hints']:
                        ua.headers.accept_ch('Sec-CH-UA-Platform-Version, Sec-CH-UA-Full-Version-List')
                        headers = ua.headers.get()

                        f.write("User-Agent: %s\n" % headers.get('user-agent'))
                        for key, value in headers.items():
                            if key != 'user-agent':
                                f.write("%s: %s\n" % (key, value))
                        f.write("\n")
                    else:
                        f.write("%s\n" % ua.headers.get().get('user-agent'))

                    written = i + 1

                    # Arayüzü saniyede ~10 kez güncelle (100k üretimde kilitlenmesin)
                    now = time.time()
                    if now - last_update >= 0.1:
                        last_update = now
                        self.ui_queue.put(('progress', written / count * 100))

            elapsed = time.time() - started
            self.ui_queue.put(('done', written, count, filepath, elapsed, self.stop_event.is_set()))

        except Exception as e:
            self.ui_queue.put(('error', str(e)))

    # ---- kuyruk yoklaması (ana thread) ----
    def _poll_queue(self):
        try:
            while True:
                message = self.ui_queue.get_nowait()
                kind = message[0]
                if kind == 'progress':
                    self.progress_var.set(message[1])
                elif kind == 'done':
                    self._on_generation_done(*message[1:])
                elif kind == 'error':
                    self._on_generation_error(message[1])
        except queue.Empty:
            pass
        except tk.TclError:
            return  # pencere kapatıldı

        try:
            self.root.after(100, self._poll_queue)
        except tk.TclError:
            pass

    # ---- arayüz güncellemeleri (her zaman ana thread'de) ----
    def _on_generation_done(self, written, requested, filepath, elapsed, cancelled):
        self.progress_var.set(0)
        self.generate_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)

        if cancelled:
            self.status_var.set("Cancelled: %d / %d written" % (written, requested))
            messagebox.showinfo("Cancelled",
                                "Generation cancelled.\n%d User-Agents saved to:\n%s"
                                % (written, filepath))
            return

        self.status_var.set("%d User-Agents in %.2f s" % (written, elapsed))
        messagebox.showinfo("Success",
                            "%d UAs created in %.2f s!\nSaved to: %s"
                            % (written, elapsed, filepath))

    def _on_generation_error(self, message):
        self.progress_var.set(0)
        self.generate_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.status_var.set("Error")
        messagebox.showerror("Error", "Error:\n%s" % message)

    def cancel_generation(self):
        self.stop_event.set()
        self.status_var.set("Cancelling...")
        self.cancel_button.config(state=tk.DISABLED)

    def on_close(self):
        # Kapanırken işçi thread'i durdur
        self.stop_event.set()
        self.root.destroy()

    def on_device_change(self, *args):
        self.update_platform_options()


if __name__ == "__main__":
    root = tk.Tk()
    app = UAGeneratorApp(root)
    root.mainloop()
