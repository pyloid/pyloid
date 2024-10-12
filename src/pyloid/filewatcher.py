from PySide6.QtCore import QFileSystemWatcher, QObject, Signal

class FileWatcher(QObject):
    file_changed = Signal(str)
    directory_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.file_changed)
        self.watcher.directoryChanged.connect(self.directory_changed)

    def add_path(self, path):
        """Add a file or directory to the watch list."""
        return self.watcher.addPath(path)

    def remove_path(self, path):
        """Remove a file or directory from the watch list."""
        return self.watcher.removePath(path)

    def get_watched_paths(self):
        """Return all currently watched paths (files + directories)."""
        return self.watcher.files() + self.watcher.directories()
      
    def get_watched_files(self):
        """Return all currently watched files."""
        return self.watcher.files()
    
    def get_watched_directories(self):
        """Return all currently watched directories."""
        return self.watcher.directories()
    
    def remove_all_paths(self):
        """Remove all paths from the watch list."""
        return self.watcher.removePaths(self.get_watched_paths())
