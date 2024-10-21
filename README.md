# Pyloid 👋

Pyloid is the Python backend version of Electron and Tauri, designed to simplify desktop application development. This open-source project, built on **QtWebEngine** and **PySide6**, provides seamless integration with various Python features, making it easy to build powerful applications effortlessly.

![example image](example.png)

## 🚀 Why Pyloid?

With Pyloid, you can leverage the full power of Python in your desktop applications. Its simplicity and flexibility make it the perfect choice for both beginners and experienced developers looking for a Python-focused alternative to Electron or Tauri. It is especially optimized for building AI-powered desktop applications.

## Key Features 🚀

- **Web-based GUI Generation**: Easily build the UI for desktop applications using HTML, CSS, and JavaScript.
- **System Tray Icon Support** 🖥️: Implement system tray icons with ease to add various utilities to your app.
- **Multi-Window Management**: Create and manage multiple windows effortlessly.
- **Bridge API between Python and JavaScript** 🌉: Facilitates smooth communication between Python and JavaScript to integrate various functionalities.
- **Single Instance Application Support**: Prevents duplicate app instances and manages applications with a single instance.
- **Comprehensive Desktop App Features**: Provides a wide range of functions for desktop apps, including monitor management, desktop capture, notifications, shortcuts, and clipboard access.
- **Clean and Intuitive Code Structure**: Offers a simple and readable code structure that enhances developer productivity.
- **Live UI Development Experience**: Experience real-time UI updates as you modify your code, providing an efficient development workflow.
- **Cross-Platform Support**: Runs on various operating systems, including Windows, macOS, and Linux.
- **Integration with Various Frontend Libraries**: Supports integration with frontend frameworks like HTML/CSS/JS and React.

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
