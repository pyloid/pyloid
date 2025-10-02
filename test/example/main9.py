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


from pyloid.thread_pool import (
	PyloidThreadPool,
	PyloidRunnable,
	PyloidDefaultSignals,
)
import time


class ProgressWorker(PyloidRunnable):
	def __init__(self):
		super().__init__()
		self.signals = PyloidDefaultSignals()

	def run(self) -> None:
		for i in range(1001):
			# print(f"진행률: {i}%")
			self.signals.progress.emit(i)
			time.sleep(0.1)


# ThreadPool 사용
thread_pool = PyloidThreadPool()
worker = ProgressWorker()

thread_pool.start(worker, 5)

worker.signals.finished.connect(lambda: print('작업이 완료되었습니다.'))
worker.signals.error.connect(lambda error: print(f'에러 발생: {error}'))
worker.signals.progress.connect(lambda progress: print(f'진행률: {progress}%'))

print(thread_pool.active_thread_count())

app.run()
