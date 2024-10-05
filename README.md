# Pylon 💎

Pylon is a framework that allows you to easily create desktop applications using Python and web technologies. 🐍🌐

## Key Features 🚀

- Web-based GUI generation
- System tray icon support 🖥️
- Multi-window management 🪟
- Bridge API between Python and JavaScript 🌉
- Single instance application support

## Installation 📦

### Direct Installation

```bash
pip install pylon-app
```

### Creating a React + Pylon Project

Boilerplate address: [https://github.com/python-pylon/pylon-react-boilerplate](https://github.com/python-pylon/pylon-react-boilerplate)

## Usage 🛠️

### Creating a Basic Application

```python
from pylon import PylonApp

app = PylonApp(single_instance=True, icon_path="assets/icon.ico")

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

```python
from pylon import PylonAPI, Bridge

class CustomAPI(PylonAPI):
    @Bridge(str, int, result=str)
    def echo(self, message, number):
        return f"Message received in Python: {message}, {number}"

    @Bridge(result=str)
    def getAppVersion(self):
        return "1.0.0"

    @Bridge(result=str)
    def create_window(self):
        window = app.create_window(
            "alert.html",
            js_apis=[CustomAPI()],
            width=300,
            height=200,
            x=100,
            y=100,
        )
        return window.id

window = app.create_window(
    "index.html",
    js_apis=[CustomAPI()],
    # Other options...
)
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

  // Using the create_window method
  pylon.CustomAPI.create_window().then((windowId) => {
    console.log('New window ID:', windowId); // "New window ID: [generated window ID]" output
  });

  // Example using async/await syntax
  async function useCustomAPI() {
    try {
      const echoResult = await pylon.CustomAPI.echo('Test', 100);
      console.log(echoResult);

      const appVersion = await pylon.CustomAPI.getAppVersion();
      console.log('Current app version:', appVersion);

      const newWindowId = await pylon.CustomAPI.create_window();
      console.log('Newly created window ID:', newWindowId);
    } catch (error) {
      console.error('Error occurred during API call:', error);
    }
  }

  useCustomAPI();
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

## API Reference 📚

### PylonApp

- `create_window(url, title, frame, context_menu, js_apis, enable_dev_tools, width, height, x, y) -> BrowserWindow`: Creates a new window and returns a BrowserWindow object.
- `run()`: Runs the application.
- `set_tray_actions(actions)`: Sets tray icon actions.
- `set_tray_menu_items(items)`: Sets tray menu items.
- `setup_tray()`: Sets up the system tray.
- `get_windows()`: Returns a list of all browser windows.
- `show_main_window()`: Shows the first window.
- `get_window_by_id(window_id)`: Returns the window with the given ID.
- `hide_window_by_id(window_id)`: Hides the window with the given ID.
- `show_window_by_id(window_id)`: Shows the window with the given ID.
- `close_window_by_id(window_id)`: Closes the window with the given ID.
- `close_all_windows()`: Closes all windows.
- `quit()`: Quits the application.
- `toggle_fullscreen_by_id(window_id)`: Toggles fullscreen mode for the window with the given ID.
- `minimize_window_by_id(window_id)`: Minimizes the window with the given ID.
- `maximize_window_by_id(window_id)`: Maximizes the window with the given ID.
- `restore_window_by_id(window_id)`: Restores the window with the given ID to its normal state.

### BrowserWindow

- `__init__(app, title, url, frame, context_menu, js_apis, enable_dev_tools, width, height, x, y)`: Initializes a new browser window.
- `load_html_file(file_path)`: Loads a local HTML file into the web view.
- `_on_load_finished(ok)`: Handles the event when the web page load is finished.
- `open_dev_window()`: Opens the developer tools window.
- `get_window_properties()`: Returns the properties of the window.
- `closeEvent(event)`: Handles the event when the window is closed.
- `hide_window()`: Hides the window.
- `show_window()`: Shows the window.
- `close_window()`: Closes the window.
- `toggle_fullscreen()`: Toggles fullscreen mode for the window.
- `minimize_window()`: Minimizes the window.
- `maximize_window()`: Maximizes the window.
- `restore_window()`: Restores the window to its normal state.

### PylonAPI

Used to define bridge APIs for communication between Python and JavaScript.

- `@Bridge(*arg_types, result=return_type)`: Converts a Python method into a function callable from JavaScript.
  - `arg_types`: Types of function arguments (multiple possible)
  - `result`: Type of return value (optional)

## License 📄

This project is licensed under the terms of the Apache License 2.0. See the [LICENSE](./LICENSE) file for details.

## Contributing 🤝

(Add information about how to contribute here)
