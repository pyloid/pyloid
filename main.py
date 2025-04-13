from src.pyloid.pyloid import Pyloid
from src.pyloid.serve import pyloid_serve

# Pyloid 앱 생성 및 설정
app_instance = Pyloid(app_name="Pyloid-App", single_instance=False, data={"port": 8000})
app_instance.set_icon("assets/icon.png")
app_instance.set_tray_icon("assets/icon.png")

url = pyloid_serve(directory="file/build-next")

store = app_instance.store("store.json")
print(store.get("test"))

store.save()

window = app_instance.create_window("Pyloid-App")
window.load_url(url)
window.show_and_focus()
window.set_dev_tools(True)

app_instance.run()
