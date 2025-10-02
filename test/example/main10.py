from pyloid.pyloid import (
	Pyloid,
)
from pyloid.utils import (
	is_production,
	get_production_path,
)
import os

app = Pyloid(
	app_name='Pyloid-App',
	single_instance=True,
)

if is_production():
	app.set_icon(
		os.path.join(
			get_production_path(),
			'icon.ico',
		)
	)
	app.set_tray_icon(
		os.path.join(
			get_production_path(),
			'icon.ico',
		)
	)
else:
	app.set_icon(
		'assets/icon.ico'
	)
	app.set_tray_icon(
		'assets/icon.ico'
	)

win = app.create_window(
	'main2'
)


win.set_dev_tools(
	True
)

if is_production():
	win.load_file(
		os.path.join(
			get_production_path(),
			'file/index6.html',
		)
	)
else:
	win.load_file(
		'file/index6.html'
	)

win.show_and_focus()


from pyloid.thread_pool import (
	PyloidThreadPool,
	PyloidRunnable,
)
import time


class Worker(
	PyloidRunnable
):
	def run(
		self,
	):
		time.sleep(
			1
		)
		print(
			'예약된 스레드에서 작업 실행'
		)


# 스레드 풀 생성
thread_pool = PyloidThreadPool()

# 스레드 예약
thread_pool.reserve_thread()


# 예약된 스레드에서 작업 실행
worker = Worker()
thread_pool.start_on_reserved_thread(
	worker
)

# 작업이 완료될 때까지 대기
if thread_pool.wait_for_done():
	# 중요: 예약된 스레드는 반드시 해제해야 함
	print(
		'작업이 완료되었습니다.'
	)
	thread_pool.release_thread()

print(
	thread_pool.active_thread_count()
)

app.run()
