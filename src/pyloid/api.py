from PySide6.QtCore import QObject, Slot

class PyloidAPI(QObject):
    """
    PyloidAPI 클래스는 PySide6의 QObject를 상속받아 생성된 클래스입니다.
    JavaScript와 Python 간의 통신을 가능하게 합니다.

    사용 예제
    --------
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
    Bridge 함수는 JavaScript에서 호출할 수 있는 슬롯을 생성합니다.

    Parameters
    ----------
    *args : tuple
        가변 인자 목록입니다.
    **kwargs : dict
        키워드 인자 목록입니다.

    사용 예제
    --------
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
