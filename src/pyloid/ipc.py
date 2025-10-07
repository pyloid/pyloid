from PySide6.QtCore import (
	QObject,
	Slot,
)
from typing import (
	TYPE_CHECKING,
)

if TYPE_CHECKING:
	from pyloid.pyloid import (
		Pyloid,
	)
	from pyloid.browser_window import (
		BrowserWindow,
	)


class PyloidIPC(QObject):
	"""
	PyloidIPC class.
	It enables communication between JavaScript and Python via IPC.

	Usage Example
	-------------
	(Python)
	```python
	from pyloid import Pyloid
	from pyloid.ipc import PyloidIPC, Bridge

	app = Pyloid('Pyloid-App')

	class CustomIPC(PyloidIPC):
		@Bridge(str, result=str)
		def echo(self, message):
			return f'Message received in Python: {message}'

		@Bridge(int, int, result=int)
		def add(self, a, b):
			return a + b

		@Bridge(result=str)
		def create_window(self):
			win = self.pyloid.create_window(title='Pyloid Browser')
			win.load_url('https://www.google.com')
			win.show()
			win.focus()
			return win.get_id()

	# Create main window
	window = app.create_window(
		title='Pyloid Browser',
		ipc=[CustomIPC()],
	)

	window.load_file('index.html')
	window.show()
	window.focus()

	app.run()
	```
 
	---
 
	(JavaScript)
	```javascript
	import { ipc } from 'pyloid-js';

	let result = await ipc.CustomIPC.echo('Hello, Pyloid!').then((result) => {
		console.log(result); // "Message received in Python: Hello, Pyloid!"
	})

	let sum = await ipc.CustomIPC.add(5, 3).then((sum) => {
		console.log(sum); // 8
	})

	let window_id = await ipc.CustomIPC.create_window().then((window_id) => {
		console.log(window_id); // "eae338a3-c8cb-4103-852f-404486beea0d"
	})
	```
	"""

	def __init__(
		self,
	):
		super().__init__()
		self.window_id: str = None
		self.window: 'BrowserWindow' = None
		self.pyloid: 'Pyloid' = None


def Bridge(
	*args,
	**kwargs,
):
	"""
	Bridge function creates a slot that can be IPC from JavaScript.

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
	from pyloid import Pyloid
	from pyloid.ipc import PyloidIPC, Bridge

	app = Pyloid('Pyloid-App')

	class CustomIPC(PyloidIPC):
		@Bridge(str, result=str)
		def echo(self, message):
			return f'Message received in Python: {message}'

		@Bridge(int, int, result=int)
		def add(self, a, b):
			return a + b

		@Bridge(result=str)
		def create_window(self):
			win = self.pyloid.create_window(title='Pyloid Browser')
			win.load_url('https://www.google.com')
			win.show()
			win.focus()
			return win.get_id()

	# Create main window
	window = app.create_window(
		title='Pyloid Browser',
		ipc=[CustomIPC()],
	)

	window.load_file('index.html')
	window.show()
	window.focus()

	app.run()
	```
	---
	(JavaScript)
	```javascript
	import { ipc } from 'pyloid-js';

	let result = await ipc.CustomIPC.echo('Hello, Pyloid!').then((result) => {
		console.log(result); // "Message received in Python: Hello, Pyloid!"
	})

	let sum = await ipc.CustomIPC.add(5, 3).then((sum) => {
		console.log(sum); // 8
	})

	let window_id = await ipc.CustomIPC.create_window().then((window_id) => {
		console.log(window_id); // "eae338a3-c8cb-4103-852f-404486beea0d"
	})
	```
	"""
	return Slot(
		*args,
		**kwargs,
	)
