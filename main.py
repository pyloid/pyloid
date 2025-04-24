from src.pyloid.pyloid import Pyloid
from src.pyloid.serve import pyloid_serve
from src.pyloid.rpc import PyloidRPC, RPCContext
from src.pyloid.tray import TrayEvent
from asyncio import sleep

rpc = PyloidRPC()


@rpc.method()
async def hello(ctx: RPCContext):
    print(ctx.window.get_title())
    await sleep(3)
    print("hello")
    return "Hello, World!"


@rpc.method()
async def hello2():
    await sleep(10)
    print("hello2")
    return "Hello, World2!"


print(rpc.url)

# Pyloid 앱 생성 및 설정
app_instance = Pyloid(app_name="Pyloid-App", single_instance=False)
app_instance.set_icon("assets/icon.png")
app_instance.set_tray_icon("assets/icon.png")

# url = pyloid_serve(directory="file/build-next")

# store = app_instance.store("store.json")
# print(store.get("test"))

# store.save()

window = app_instance.create_window("Pyloid-App")
window.load_url("chrome://gpu")
window.show_and_focus()
window.set_dev_tools(True)


def on_double_click():
    app_instance.show_main_window()
    app_instance.show_and_focus_main_window()


app_instance.set_tray_actions(
    {
        TrayEvent.DoubleClick: on_double_click,
    }
)
app_instance.set_tray_menu_items(
    [
        {"label": "Show Window", "callback": app_instance.show_and_focus_main_window},
        {"label": "Exit", "callback": app_instance.quit},
    ]
)

app_instance.run()
