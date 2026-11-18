# AgentX: Advanced User-Agent Generator 🚀

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code Style: PEP8](https://img.shields.io/badge/code%20style-PEP8-brightgreen)](https://peps.python.org/pep-0008/)

**A powerful and efficient tool for generating unlimited, realistic User-Agents across all platforms.**

AgentX is designed for developers, QA engineers, and cybersecurity professionals who need precise control over User-Agent strings. With its intuitive GUI and robust engine, AgentX makes it easy to generate authentic User-Agent lists for testing, analysis, and automation.

---

## 🔥 Features
- ✅ **High-Volume Generation** – Up to 100,000 User-Agent strings per run
- ✅ **Cross-Platform Support** – Generate UA strings for Windows, macOS, Linux, Android, and iOS
- ✅ **Browser Selection** – Chrome, Edge, Firefox, and Safari support
- ✅ **Batch Processing** – Generate thousands of UA strings at once
- ✅ **Easy-to-Use GUI** – Simple, intuitive interface for quick generation
- ✅ **Standalone & Portable** – No installation required
- ✅ **Random Device Selection** – Automatically chooses device, platform, and browser
- ✅ **Client Hints Support** – Writes all headers (UA + CH) to file when enabled
- ✅ **Weighted Browser Versions** – Browser versions are distributed according to real traffic patterns
- ✅ **Cancelable Generation** – Stop a running job at any time; whatever was written stays on disk
- ✅ **Live Status Bar** – Progress and result count are shown without freezing the window
- ✅ **Thread-Safe UI** – Generation runs in a worker thread and never touches tkinter directly


---

## 🖥️ Screenshots

<img width="507" height="438" alt="Ekran görüntüsü 2025-10-26 130626" src="https://github.com/user-attachments/assets/9d3a7481-a114-4179-8507-6c3840b984b6" />

---

## ⚙️ Technical Specifications
### Dependencies
Core Engine: ua-generator==2.1.9

GUI Framework: tkinter (bundled with Python — no pip package)

That is the complete dependency list. `gzip` and `pyOpenSSL` are not used by AgentX;
earlier versions of this README listed them by mistake.

Install with:
```bash
pip install -r requirements.txt
```

### System Requirements
- **OS**: Windows 10/11, macOS, Linux (64-bit)
- **Python**: 3.9 or newer (required by ua-generator 2.1.9)
- **Hardware**: Minimum 4GB RAM, 2GHz CPU
- **Internet**: Not required — User-Agents are generated locally from bundled templates

---

## 📥 Download
- **[AgentX.exe — v1.4, 10.0 MB](https://github.com/cangurel81/Agentx/releases/latest/download/AgentX.exe)** – Standalone Windows executable, Python is not required
- **Source Code (zip/tar.gz)** – Available on GitHub

> Windows SmartScreen may warn about an unsigned binary — choose **More info → Run anyway**.

---

## 🚀 Installation & Usage

### Option 1 — Prebuilt executable
1. **Download** AgentX from the releases section
2. **Run the application** – No installation required

### Option 2 — From source
```bash
git clone https://github.com/cangurel81/Agentx.git
cd Agentx
pip install -r requirements.txt
python user_agents_gui.py
```

### Using the app
1. **Select Device Type** – Desktop, Mobile or Random (Random enables every platform and browser)
2. **Pick platforms and browsers** – the platform list follows the selected device type
3. **Set the count** – 1 to 100,000 per run
4. **Choose a save location** – if left empty, a timestamped file is written to the Desktop
5. **Click "Generate User Agents"** – the progress bar and status line update live
6. **Cancel** stops the job immediately; the partially written file is kept

Output format: one User-Agent per line. With **Client Hints** enabled every entry becomes a
header block (`User-Agent: ...` plus `Sec-CH-UA-*` lines) separated by a blank line.

---

## 💡 Support & Documentation
For support, updates, and detailed documentation, visit **[WebAdHere Technologies](https://webadhere.com)**.

