from PySide6.QtCore import QFileSystemWatcher, QObject, Signal


class FileWatcher(QObject):
	"""
	FileWatcher class for monitoring file and directory changes.

	This class automatically detects changes in specific files or directories and provides notifications.

	Attributes
	----------
	file_changed : Signal
	    Signal emitted when a file is changed.
	directory_changed : Signal
	    Signal emitted when a directory is changed.

	Methods
	-------
	add_path(path)
	    Adds a file or directory to the watch list.
	remove_path(path)
	    Removes a file or directory from the watch list.
	get_watched_paths()
	    Returns all currently watched paths (files and directories).
	get_watched_files()
	    Returns all currently watched files.
	get_watched_directories()
	    Returns all currently watched directories.
	remove_all_paths()
	    Removes all paths from the watch list.
	"""

	file_changed = Signal(str)
	directory_changed = Signal(str)

	def __init__(self):
		"""
		Initializes the FileWatcher object.
		"""
		super().__init__()
		self.watcher = QFileSystemWatcher()
		self.watcher.fileChanged.connect(self.file_changed)
		self.watcher.directoryChanged.connect(self.directory_changed)

	def add_path(self, path):
		"""
		Adds a file or directory to the watch list.

		Parameters
		----------
		path : str
		    The path of the file or directory to watch.

		Returns
		-------
		bool
		    Whether the path was successfully added.

		Examples
		--------
		>>> watcher = FileWatcher()
		>>> result = watcher.add_path('/path/to/file_or_directory')
		>>> if result:
		>>>     print("Watch started")
		>>> else:
		>>>     print("Failed to start watching")
		"""
		return self.watcher.addPath(path)

	def remove_path(self, path):
		"""
		Removes a file or directory from the watch list.

		Parameters
		----------
		path : str
		    The path of the file or directory to remove.

		Returns
		-------
		bool
		    Whether the path was successfully removed.

		Examples
		--------
		>>> watcher = FileWatcher()
		>>> result = watcher.remove_path('/path/to/file_or_directory')
		>>> if result:
		>>>     print("Successfully stopped watching")
		>>> else:
		>>>     print("Failed to stop watching")
		"""
		return self.watcher.removePath(path)

	def get_watched_paths(self):
		"""
		Returns all currently watched paths (files and directories).

		Returns
		-------
		list of str
		    All currently watched paths.

		Examples
		--------
		>>> watcher = FileWatcher()
		>>> paths = watcher.get_watched_paths()
		>>> print('Watched paths:', paths)
		"""
		return self.watcher.files() + self.watcher.directories()

	def get_watched_files(self):
		"""
		Returns all currently watched files.

		Returns
		-------
		list of str
		    All currently watched files.

		Examples
		--------
		>>> watcher = FileWatcher()
		>>> files = watcher.get_watched_files()
		>>> print('Watched files:', files)
		"""
		return self.watcher.files()

	def get_watched_directories(self):
		"""
		Returns all currently watched directories.

		Returns
		-------
		list of str
		    All currently watched directories.

		Examples
		--------
		>>> watcher = FileWatcher()
		>>> directories = watcher.get_watched_directories()
		>>> print('Watched directories:', directories)
		"""
		return self.watcher.directories()

	def remove_all_paths(self):
		"""
		Removes all paths from the watch list.

		Returns
		-------
		bool
		    Whether all paths were successfully removed.

		Examples
		--------
		>>> watcher = FileWatcher()
		>>> result = watcher.remove_all_paths()
		>>> if result:
		>>>     print("Successfully removed all paths")
		>>> else:
		>>>     print("Failed to remove all paths")
		"""
		return self.watcher.removePaths(self.get_watched_paths())
