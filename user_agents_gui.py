import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ua_generator
from datetime import datetime
import threading
from ua_generator.options import Options

class UAGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AgentX: Advanced User-Agent Generator with GUI")
        self.root.geometry("500x400")
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
        self.is_random = False
        
        self.create_widgets()
        self.update_platform_options()
        self.device_var.trace_add('write', self.on_device_change)

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

        ttk.Button(main_frame, text="Generate User Agents", 
                 command=self.start_generation).pack(pady=10)

        footer = ttk.Frame(main_frame)
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        ttk.Label(footer, text="WebAdHere Technologies", font=('Tahoma', 8)).pack(side=tk.LEFT)
        ttk.Label(footer, text="AgentX v1.3", font=('Tahoma', 8)).pack(side=tk.RIGHT)

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

    def choose_file(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialdir=os.path.join(os.path.expanduser('~'), 'Desktop'),
            filetypes=[("Text files", "*.txt")]
        )
        if path:
            self.filepath_var.set(path)

    def start_generation(self):
        threading.Thread(target=self.generate_agents, daemon=True).start()

    def generate_agents(self):
        try:
            count = self.count_var.get()
            filepath = self.filepath_var.get() or os.path.join(
                os.path.expanduser('~'), 'Desktop',
                f'UserAgents_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            )

            if self.device_var.get() == 'random':
                device_type = None  
            else:
                device_type = self.device_var.get()  

            platforms = tuple(p for p, var in self.platform_vars.items() if var.get())
            browsers = tuple(b for b, var in self.browser_vars.items() if var.get())

            if not platforms:
                messagebox.showerror("Error", "Please select at least one platform!")
                return
            
            if not browsers:
                messagebox.showerror("Error", "Please select at least one browser!")
                return

            options = Options() if self.weighted_versions_var.get() else None
            if options:
                options.weighted_versions = True
            
            with open(filepath, 'w', encoding='utf-8') as f:
                for i in range(count):
                    ua = ua_generator.generate(
                        device=device_type,
                        platform=platforms,
                        browser=browsers,
                        options=options
                    )
                    
                    if self.client_hints_var.get():
                        ua.headers.accept_ch('Sec-CH-UA-Platform-Version, Sec-CH-UA-Full-Version-List')
                        
                        headers = ua.headers.get()
                        
                        f.write(f"User-Agent: {headers.get('user-agent')}\n")
                        
                        for key, value in headers.items():
                            if key != 'user-agent': 
                                f.write(f"{key}: {value}\n")
                        
                        f.write("\n") 
                    else:
                        ua_string = ua.headers.get().get('user-agent')
                        f.write(f"{ua_string}\n")
                    
                    self.progress_var.set((i+1)/count*100)

            messagebox.showinfo("Success", f"{count} UAs created!\nSaved to: {filepath}")
            self.progress_var.set(0)

        except Exception as e:
            messagebox.showerror("Error", f"Error:\n{str(e)}")
            self.progress_var.set(0)

    def on_device_change(self, *args):
        self.update_platform_options()

if __name__ == "__main__":
    root = tk.Tk()
    app = UAGeneratorApp(root)
    root.mainloop()