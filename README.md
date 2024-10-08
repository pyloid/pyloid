# Pylon 👋

Pylon is the Python backend version of Electron and Tauri, designed to simplify desktop application development. This open-source project provides seamless integration with various Python features, making it easy to build powerful applications effortlessly.

## 🚀 Why Pylon?

With Pylon, you can leverage the full power of Python in your desktop applications. Its simplicity and flexibility make it the perfect choice for both beginners and experienced developers looking for a Python-focused alternative to Electron or Tauri. It is especially optimized for building AI-powered desktop applications.

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

[Pylon Documentation](https://docs.pylon-app.com/)

### Create Project 📦

#### Creating a HTML/CSS/JS + Pylon Project 🌐

[https://github.com/python-pylon/pylon-html-boilerplate](https://github.com/python-pylon/pylon-html-boilerplate)

#### Creating a React + Vite + Pylon Project ⚛️

[https://github.com/python-pylon/pylon-react-boilerplate](https://github.com/python-pylon/pylon-react-boilerplate)

### Custom Your Boilerplate 🔨

```bash
pip install pylon-app
```

Package URL: [https://pypi.org/project/pylon-app/](https://pypi.org/project/pylon-app/)

## Usage 🛠️

### Creating a Basic Application

```python
from pylon import PylonApp

app = PylonApp(single_instance=True)

# set icon
if (is_production()):
    app.set_icon(os.path.join(get_production_path(), "icons/icon.png"))
else:
    app.set_icon("src-pylon/icons/icon.png")

# create window
window = app.create_window(
    title="Pylon Browser1",
    js_apis=[CustomAPI()],
    dev_tools=True
)

window.set_size(800, 600)

# load html
if (is_production()):
    window.set_dev_tools(False)
    window.load_file(os.path.join(get_production_path(), "src/index.html"))
else:
    window.load_file("src/index.html")

# show window
window.show_and_focus()

app.run()
```

### Setting Up System Tray

```python
from pylon import TrayEvent

def on_double_click():
    print("Tray icon was double-clicked.")

app.set_tray_actions({
    TrayEvent.DoubleClick: on_double_click,
})
app.set_tray_menu_items([
    {"label": "Show Window", "callback": app.show_main_window},
    {"label": "Quit", "callback": app.quit},
])
app.setup_tray()
```

```javascript
// CustomAPI method usage example
document.addEventListener('pylonReady', function () {
  // Using the echo method
  pylon.CustomAPI.echo('Hello', 42).then((result) => {
    console.log(result); // "Message received in Python: Hello, 42" output
  });

  // Using the getAppVersion method
  pylon.CustomAPI.getAppVersion().then((version) => {
    console.log('App version:', version); // "App version: 1.0.0" output
  });

  // Example using async/await syntax
  async function useCustomAPI() {
    const echoResult = await pylon.CustomAPI.echo('Test', 100);
    console.log(echoResult);

    const appVersion = await pylon.CustomAPI.getAppVersion();
    console.log('Current app version:', appVersion);
  }

  useCustomAPI();

  // Button click event binding
  document.getElementById('myButton').addEventListener('click', function () {
    // Using the create_window method
    pylon.CustomAPI.create_window().then((windowId) => {
      console.log('New window ID:', windowId); // "New window ID: [generated window ID]" output
    });
  });
});
```

### Using React

```javascript
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './index.css';

document.addEventListener('pylonReady', function () {
  createRoot(document.getElementById('root')).render(
    <StrictMode>
      <App />
    </StrictMode>
  );
});

function App() {
  console.log('Pylon is ready');

  window.pylon.CustomAPI.getAppVersion().then((version) => {
    console.log('App version:', version); // "App version: 1.0.0"
  });
  return <h1>Hello World</h1>;
}
```

## License 📄

This project is licensed under the terms of the Apache License 2.0. See the [LICENSE](./LICENSE) file for details.

This project uses PySide6, which is licensed under the LGPL (Lesser General Public License).

## Contributing 🤝

(Add information about how to contribute here)
