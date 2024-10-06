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

## Installation 📦

### Direct Installation

```bash
pip install pylon-app
```

Package URL: [https://pypi.org/project/pylon-app/](https://pypi.org/project/pylon-app/)

### Creating a React + Pylon Project

Boilerplate address: [https://github.com/python-pylon/pylon-react-boilerplate](https://github.com/python-pylon/pylon-react-boilerplate)

## Usage 🛠️

### Creating a Basic Application

```python
from pylon import PylonApp

app = PylonApp(single_instance=True)

app.set_icon("assets/icon.ico")

window = app.create_window(
    "https://www.example.com",
    title="Pylon Browser",
)

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

### Creating Python-JavaScript Bridge API

````python
from pylon import PylonAPI, Bridge

class CustomAPI(PylonAPI):
    @Bridge(str, int, result=str)
    def echo(self, message, message2):
        print(f"Message: {message}-{message2}")
        return f"Message received in Python: {message}-{message2}"

    @Bridge(result=str)
    def getAppVersion(self):
        return "1.0.0"

    @Bridge(result=str)
    def create_window(self):
        window = app.create_window(
            title="Pylon Browser2",
            frame=True,
            context_menu=False,
            js_apis=[CustomAPI()],
            dev_tools=True
        )


        window.set_size(800, 600)
        window.set_position(0, 0)
        window.load_url("https://www.google.com")
        window.show()
        window.focus()

        return window.id

window = app.create_window(
    title="Pylon Browser1",
    frame=True,
    context_menu=False,
    js_apis=[CustomAPI()],
    dev_tools=True
)

window.set_size(1500, 1000)

if (is_production()):
    window.load_file(os.path.join(get_production_path() + "/file/index.html"))
else:
    window.load_file("file/index.html")

window.show_and_focus()

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
````

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
