from src.pyloid.pyloid import (
	Pyloid,
)
import asyncio
import threading

app = Pyloid(app_name='Pyloid-App')

window = app.create_window('Pyloid-App')
window.load_file('file/index.html')
window.show_and_focus()


async def async_tasks():
	await asyncio.sleep(5)

	await asyncio.to_thread(
		window.set_title,
		'Hello, World!',
	)

	title = await asyncio.to_thread(window.get_title)

	print(title)


def run_other_async_tasks():
	asyncio.run(async_tasks())


async_thread = threading.Thread(
	target=run_other_async_tasks,
	daemon=True,
)

async_thread.start()


app.run()
