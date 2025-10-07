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
	from pyloid import (
	    Pyloid,
	)
	from pyloid.ipc import (
	    PyloidIPC,
	    Bridge,
	)

	app = Pyloid('Pyloid-App')


	class CustomIPC(PyloidIPC):
	    @Bridge(
	        str,
	        result=str,
	    )
	    def echo(
	        self,
	        message,
	    ):
	        return f'Message received in Python: {message}'


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
	let result = await window.pyloid.CustomIPC.echo('Hello, Pyloid!');
	console.log(result);
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
	from pyloid import (
	    Pyloid,
	    PyloidIPC,
	    Bridge,
	)

	app = Pyloid('Pyloid-App')


	class CustomIPC(PyloidIPC):
	    @Bridge(
	        str,
	        result=str,
	    )
	    def echo(
	        self,
	        message,
	    ):
	        return f'Message received in Python: {message}'


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
	let result = await window.pyloid.CustomIPC.echo('Hello, Pyloid!');
	console.log(result);
	```
	"""
	return Slot(
		*args,
		**kwargs,
	)
