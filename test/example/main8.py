from pyloid.pyloid import Pyloid
from pyloid.utils import is_production, get_production_path
import os

app = Pyloid(app_name='Pyloid-App', single_instance=True)

if is_production():
	app.set_icon(os.path.join(get_production_path(), 'icon.ico'))
	app.set_tray_icon(os.path.join(get_production_path(), 'icon.ico'))
else:
	app.set_icon('assets/icon.ico')
	app.set_tray_icon('assets/icon.ico')

win = app.create_window('main2')


win.set_dev_tools(True)

if is_production():
	win.load_file(os.path.join(get_production_path(), 'file/index6.html'))
else:
	win.load_file('file/index6.html')

win.show_and_focus()


from pyloid.thread_pool import ThreadPool
import time


def progress_worker():
	for i in range(1001):
		print(f'진행률: {i}%')
		time.sleep(0.1)


# ThreadPool 사용
thread_pool = ThreadPool()

thread_pool.start(progress_worker, 5)

print(thread_pool.active_thread_count())

app.run()
