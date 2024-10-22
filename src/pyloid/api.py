from PySide6.QtCore import QObject, Slot


class PyloidAPI(QObject):
    """
    PyloidAPI class is derived from PySide6's QObject.
    It enables communication between JavaScript and Python.

    Usage Example
    -------------
    (Python)
    ```python
    from pyloid import Pyloid, PyloidAPI, Bridge

    app = Pyloid("Pyloid-App")

    class CustomAPI(PyloidAPI):
        @Bridge(str, result=str)
        def echo(self, message):
            return f"Message received in Python: {message}"

    # Create main window
    window = app.create_window(
        title="Pyloid Browser",
        js_apis=[CustomAPI()],
    )

    window.load_file("index.html")

    window.show()
    window.focus()

    app.run()
    ```
    ---
    (JavaScript)
    ```javascript
    document.addEventListener('pyloidReady', async function () {
        let result = await window.pyloid.CustomAPI.echo('Hello, Pyloid!');
        console.log(result);
    });
    ```

    """

    def __init__(self):
        super().__init__()


def Bridge(*args, **kwargs):
    """
    Bridge function creates a slot that can be called from JavaScript.

    Parameters
    ----------
    *args : tuple
        Variable length argument list.
    **kwargs : dict
        Arbitrary keyword arguments.

    Usage Example
    -------------
    (Python)
    ```python
    from pyloid import Pyloid, PyloidAPI, Bridge

    app = Pyloid("Pyloid-App")

    class CustomAPI(PyloidAPI):
        @Bridge(str, result=str)
        def echo(self, message):
            return f"Message received in Python: {message}"

    # Create main window
    window = app.create_window(
        title="Pyloid Browser",
        js_apis=[CustomAPI()],
    )

    window.load_file("index.html")

    window.show()
    window.focus()

    app.run()
    ```
    ---
    (JavaScript)
    ```javascript
    document.addEventListener('pyloidReady', async function () {
        let result = await window.pyloid.CustomAPI.echo('Hello, Pyloid!');
        console.log(result);
    });
    ```
    """
    return Slot(*args, **kwargs)
