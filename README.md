# Pyloid 👋

Pyloid is the Python backend version of Electron and Tauri, designed to simplify desktop application development. This open-source project, built on **QtWebEngine** and **PySide6**, provides seamless integration with various Python features, making it easy to build powerful applications effortlessly.

![example image](example.png)

## 🚀 Why Pyloid?

With Pyloid, you can leverage the full power of Python in your desktop applications. Its simplicity and flexibility make it the perfect choice for both beginners and experienced developers looking for a Python-focused alternative to Electron or Tauri. It is especially optimized for building AI-powered desktop applications.

### Key Features 🚀

- **Web-based GUI Generation**
- **System Tray Icon Support**
- **Multi-Window Management**
- **Bridge API between Python and JavaScript**
- **Single Instance Application / Multi Instance Application Support**
- **Comprehensive Desktop App Features**
- **Clean and Intuitive Code Structure**
- **Live UI Development Experience**
- **Cross-Platform Support**
- **Integration with Various Frontend Libraries**
- **Window Customization**
- **Direct Utilization of PySide6 Features**
- **Detailed Numpy-style Docstrings**

## Documentation 📚

[Pyloid Documentation](https://docs.pyloid.com/)

### Create Project 📦

#### Creating a HTML/CSS/JS + Pyloid Project 🌐

[https://github.com/pylonic/pyloid_html_boilerplate](https://github.com/Pyloid/pyloid_html_boilerplate)

#### Creating a React + Vite + Pyloid Project ⚛️

[https://github.com/pylonic/pyloid_react_boilerplate](https://github.com/Pyloid/pyloid_react_boilerplate)

### Custom Your Boilerplate 🔨

```bash
pip install pyloid
```

Package URL: [https://pypi.org/project/pyloid/](https://pypi.org/project/pyloid/)

## Usage 🛠️

### Creating a Basic Application

```python
from pyloid import Pyloid

app = Pyloid(app_name="Pyloid-App", single_instance=True)

win = app.create_window("pyloid-example")
win.load_url("https://www.example.com")
win.show_and_focus()

app.run()
```

## License 📄

This project is licensed under the terms of the Apache License 2.0. See the [LICENSE](./LICENSE) file for details.

This project uses PySide6, which is licensed under the LGPL (Lesser General Public License).

## Contributing 🤝

(Add information about how to contribute here)
