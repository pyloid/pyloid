from src.pyloid.pyloid import Pyloid
from src.pyloid.serve import pyloid_serve
from src.pyloid.rpc import PyloidRPC
from asyncio import sleep

rpc = PyloidRPC()

@rpc.method()
async def hello():
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

print(app_instance.is_auto_start())

window = app_instance.create_window("Pyloid-App", rpc=rpc)
window.load_file("file/index.html")
window.show_and_focus()
window.set_dev_tools(True)

app_instance.run()
