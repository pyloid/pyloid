# Pylon

Pylon은 Python과 웹 기술을 사용하여 데스크톱 애플리케이션을 쉽게 만들 수 있는 프레임워크입니다.

## 주요 기능

- 웹 기반 GUI 생성
- 시스템 트레이 아이콘 지원
- 다중 창 관리
- Python과 JavaScript 간 브릿지 API
- 단일 인스턴스 애플리케이션 지원

## 설치

### 직접 설치

```bash
pip install pylon-desktop
```

### React + Pylon 프로젝트 생성

보일러플레이트 주소: [https://github.com/python-pylon/pylon-react-boilerplate](https://github.com/python-pylon/pylon-react-boilerplate)

## 사용 방법

### 기본 애플리케이션 생성

```python
from pylon import PylonApp

app = PylonApp(single_instance=True, icon_path="assets/icon.ico")

window = app.create_window(
    "https://www.example.com",
    title="Pylon Browser",
)

app.run()
```

### 시스템 트레이 설정

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

### Python-JavaScript 브릿지 API 생성

```python
from src.pylon.api import PylonAPI, Bridge

class CustomAPI(PylonAPI):
    @Bridge(str, int, result=str)
    def echo(self, message, number):
        return f"파이썬에서 받은 메시지: {message}, {number}"

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
    # 기타 옵션...
)
```

## API 참조

### PylonApp

- `create_window(url, title, frame, context_menu, js_apis, enable_dev_tools, width, height, x, y) -> BrowserWindow`: 새 창을 생성하고 BrowserWindow 객체를 반환합니다.
- `run()`: 애플리케이션을 실행합니다.
- `set_tray_actions(actions)`: 트레이 아이콘 동작을 설정합니다.
- `set_tray_menu_items(items)`: 트레이 메뉴 항목을 설정합니다.
- `setup_tray()`: 시스템 트레이를 설정합니다.
- `get_windows()`: 모든 브라우저 창의 목록을 반환합니다.
- `show_main_window()`: 첫 번째 창을 표시합니다.
- `get_window_by_id(window_id)`: 주어진 ID를 가진 창을 반환합니다.
- `hide_window_by_id(window_id)`: 주어진 ID를 가진 창을 숨깁니다.
- `show_window_by_id(window_id)`: 주어진 ID를 가진 창을 표시합니다.
- `close_window_by_id(window_id)`: 주어진 ID를 가진 창을 닫습니다.
- `close_all_windows()`: 모든 창을 닫습니다.
- `quit()`: 애플리케이션을 종료합니다.
- `toggle_fullscreen_by_id(window_id)`: 주어진 ID를 가진 창의 전체 화면 모드를 전환합니다.
- `minimize_window_by_id(window_id)`: 주어진 ID를 가진 창을 최소화합니다.
- `maximize_window_by_id(window_id)`: 주어진 ID를 가진 창을 최대화합니다.
- `restore_window_by_id(window_id)`: 주어진 ID를 가진 창을 정상 상태로 복원합니다.

### BrowserWindow

- `__init__(app, title, url, frame, context_menu, js_apis, enable_dev_tools, width, height, x, y)`: 새 브라우저 창을 초기화합니다.
- `load_html_file(file_path)`: 로컬 HTML 파일을 웹 뷰에 로드합니다.
- `_on_load_finished(ok)`: 웹 페이지 로드가 완료되었을 때 이벤트를 처리합니다.
- `open_dev_window()`: 개발자 도구 창을 엽니다.
- `get_window_properties()`: 창의 속성을 반환합니다.
- `closeEvent(event)`: 창이 닫힐 때 이벤트를 처리합니다.
- `hide_window()`: 창을 숨깁니다.
- `show_window()`: 창을 표시합니다.
- `close_window()`: 창을 닫습니다.
- `toggle_fullscreen()`: 창의 전체 화면 모드를 전환합니다.
- `minimize_window()`: 창을 최소화합니다.
- `maximize_window()`: 창을 최대화합니다.
- `restore_window()`: 창을 정상 상태로 복원합니다.

### PylonAPI

Python과 JavaScript 간의 통신을 위한 브릿지 API를 정의하는 데 사용됩니다.

- `@Bridge`: Python 메서드를 JavaScript에서 호출 가능한 함수로 변환합니다.

## 예제

더 많은 예제와 사용 사례는 프로젝트의 `examples` 디렉토리를 참조하세요.

## 라이선스

이 프로젝트는 아파치 라이선스 2.0의 조건에 따라 라이선스가 부여됩니다. 자세한 내용은 [LICENSE](./LICENSE) 파일을 참조하십시오.

## 기여

(기여 방법에 대한 정보를 여기에 추가하세요)
