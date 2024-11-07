from PySide6.QtCore import QRunnable, QThreadPool, QDeadlineTimer, QObject, Signal
from typing import Callable, Optional, Union

class PyloidRunnable(QRunnable):
    """
    A runnable task class that extends QRunnable from Qt.
    
    Defines a unit of work that can be executed in a thread pool.
    """
    
    def __init__(self):
        """
        Initializes a PyloidRunnable instance.
        
        By default, auto-delete is enabled.
        """
        super().__init__()
        self.setAutoDelete(True)
    
    def get_auto_delete(self) -> bool:
        """
        Returns whether the task is automatically deleted after completion in the thread pool.
        
        The default value is True.
        
        Returns
        -------
        bool
            True if the task is automatically deleted after completion, False if manual deletion is required
            
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidRunnable
        import time
        
        class Worker(PyloidRunnable):
            def run(self):
                time.sleep(1)
                print("Task executed")
        
        worker = Worker()
        print(worker.get_auto_delete())
        ```
        """
        return self.autoDelete()
        
    def set_auto_delete(self, value: bool) -> None:
        """
        Sets whether the task is automatically deleted after completion in the thread pool.
        
        Parameters
        ----------
        value : bool
            True to enable auto-delete after task completion, 
            False to require manual deletion
            
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidRunnable
        import time
        
        class Worker(PyloidRunnable):
            def run(self):
                time.sleep(1)
                print("Task executed")
        
        worker = Worker()
        worker.set_auto_delete(False)
        ```
        """
        self.setAutoDelete(value)

    def run(self) -> None:
        """
        Defines the actual work to be executed in the thread pool.
        
        This method must be implemented in subclasses.
        
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidRunnable, PyloidThreadPool
        import time
        
        class Worker(PyloidRunnable):
            def run(self):
                time.sleep(1)
                print("Task executed")
        
        worker = Worker()
        thread_pool = PyloidThreadPool()
        thread_pool.start(worker)
        ```
        """
        pass
    
class PyloidDefaultSignals(QObject):
    """
    Default signal class.
    
    Defines signals used for task start, completion, and error occurrence in the thread pool.
    
    Attributes
    ----------
    started : Signal
        Signal emitted when a task starts
    finished : Signal
        Signal emitted when a task completes
    error : Signal(str)
        Signal emitted when an error occurs
    progress : Signal(int)
        Signal emitted when progress changes
        
    Examples
    --------
    ```python
    from pyloid.thread_pool import PyloidRunnable, PyloidThreadPool, PyloidDefaultSignals
    import time
    
    class Worker(PyloidRunnable):
        def __init__(self):
            super().__init__()
            self.signals = PyloidDefaultSignals()

        def run(self):
            for i in range(101):
                self.signals.progress.emit(i)
                time.sleep(0.1)
                
    worker = Worker()
    
    worker.signals.finished.connect(lambda: print("Task completed."))
    worker.signals.error.connect(lambda error: print(f"Error occurred: {error}"))
    worker.signals.progress.connect(lambda progress: print(f"Progress: {progress}%"))
    
    thread_pool = PyloidThreadPool()
    thread_pool.start(worker)
    ```
    """
    started = Signal()
    finished = Signal()
    error = Signal(str)
    progress = Signal(int)
    

class PyloidThreadPool:
    def __init__(self):
        self.thread_pool = QThreadPool.globalInstance()

    def start(self, runnable: Union[PyloidRunnable, Callable], priority: int = ...) -> None:
        """
        Adds a task to the thread pool and executes it.
        
        Parameters
        ----------
        runnable : Union[PyloidRunnable, Callable]
            Task to be executed
        priority : int
            Task priority
        
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidRunnable, PyloidThreadPool
        import time
        
        class Worker(PyloidRunnable):
            def run(self):
                time.sleep(1)
                print("Task executed")
                
        worker = Worker()
        thread_pool = PyloidThreadPool()
        thread_pool.start(worker)
        ```
        """
        self.thread_pool.start(runnable, priority)

    def active_thread_count(self) -> int:
        """
        Returns the number of currently active threads.
        
        Returns
        -------
        int
            Number of currently active threads
            
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidThreadPool
        
        thread_pool = PyloidThreadPool()
        print(thread_pool.active_thread_count())
        ```
        """
        return self.thread_pool.activeThreadCount()
    
    def max_thread_count(self) -> int:
        """
        Returns the maximum number of threads that can run simultaneously in the thread pool.
        
        Returns
        -------
        int
            Maximum number of threads
            
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidThreadPool
        
        thread_pool = PyloidThreadPool()
        print(thread_pool.max_thread_count())
        ```
        """
        return self.thread_pool.maxThreadCount()

    def set_max_thread_count(self, max_thread_count: int) -> None:
        """
        Sets the maximum number of threads that can run simultaneously in the thread pool.
        
        Parameters
        ----------
        max_thread_count : int
            Maximum number of threads
        
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidThreadPool
        
        thread_pool = PyloidThreadPool()
        thread_pool.set_max_thread_count(10)
        ```
        """
        self.thread_pool.setMaxThreadCount(max_thread_count)

    def reserve_thread(self) -> None:
        """
        Reserves a thread in the thread pool.
        
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidThreadPool, PyloidRunnable
        import time

        class Worker(PyloidRunnable):
            def run(self):
                time.sleep(1)
                print("Task executed on reserved thread")

        # Create thread pool
        thread_pool = PyloidThreadPool()

        # Reserve thread
        thread_pool.reserve_thread()

        try:
            # Execute task on reserved thread
            worker = Worker()
            thread_pool.start_on_reserved_thread(worker)
            
            # Wait for task completion
            thread_pool.wait_for_done()
        finally:
            # Important: Reserved threads must be released
            thread_pool.release_thread()
        ```
        """
        self.thread_pool.reserveThread()

    def release_thread(self) -> None:
        """
        Releases a reserved thread in the thread pool.
        
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidThreadPool
        
        thread_pool = PyloidThreadPool()
        thread_pool.release_thread()
        ```
        """
        self.thread_pool.releaseThread()

    def clear(self) -> None:
        """
        Removes all pending tasks from the thread pool.
        
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidThreadPool
        
        thread_pool = PyloidThreadPool()
        thread_pool.clear()
        ```
        """
        self.thread_pool.clear()

    # def contains(self, thread: QThread) -> bool:
    #     return self.thread_pool.contains(thread)

    def get_expiry_timeout(self) -> int:
        """
        Returns the thread expiry timeout in the thread pool.
        
        Returns
        -------
        int
            Thread expiry timeout
            
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidThreadPool
        
        thread_pool = PyloidThreadPool()
        print(thread_pool.get_expiry_timeout())
        ```
        """
        return self.thread_pool.expiryTimeout()

    def set_expiry_timeout(self, expiry_timeout: int) -> None:
        """
        Sets the thread expiry timeout in the thread pool.
        
        Parameters
        ----------
        expiry_timeout : int
            Thread expiry timeout
            
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidThreadPool
        
        thread_pool = PyloidThreadPool()
        thread_pool.set_expiry_timeout(1000)
        ```
        """
        self.thread_pool.setExpiryTimeout(expiry_timeout)

    # def set_stack_size(self, stack_size: int) -> None:
    #     self.thread_pool.setStackSize(stack_size)

    # def stack_size(self) -> int:
    #     return self.thread_pool.stackSize()

    # def set_thread_priority(self, priority: QThread.Priority) -> None:
    #     self.thread_pool.setThreadPriority(priority)

    # def thread_priority(self) -> QThread.Priority:
    #     return self.thread_pool.threadPriority()

    def start_on_reserved_thread(self, runnable: QRunnable) -> None:
        """
        Executes a task on a reserved thread.
        
        Parameters
        ----------
        runnable : QRunnable
            Task to be executed
            
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidThreadPool, PyloidRunnable
        import time

        class Worker(PyloidRunnable):
            def run(self):
                time.sleep(1)
                print("Task executed on reserved thread")
                
        worker = Worker()
        thread_pool = PyloidThreadPool()
        thread_pool.reserve_thread()
        thread_pool.start_on_reserved_thread(worker)
        thread_pool.wait_for_done()
        thread_pool.release_thread()
        ```
        """
        self.thread_pool.startOnReservedThread(runnable)

    def try_start(self, runnable: Union[QRunnable, Callable]) -> bool:
        """
        Adds a new task to the thread pool and attempts to execute it immediately.
        
        Only executes the task if the thread pool has available capacity.
        Operates in a non-blocking manner and does not start the task if the thread pool is full.
        
        Parameters
        ----------
        runnable : Union[QRunnable, Callable]
            Task to be executed
            
        Returns
        -------
        bool
            True: Task successfully started
            False: Task could not be started because the thread pool is full
            
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidThreadPool, PyloidRunnable
        
        class Worker(PyloidRunnable):
            def run(self):
                print("Task executed")
                
        thread_pool = PyloidThreadPool()
        worker = Worker()
        
        if thread_pool.try_start(worker):
            print("Task started")
        else:
            print("Task could not be started because the thread pool is full")
        ```
        """
        return self.thread_pool.tryStart(runnable)

    def try_take(self, runnable: QRunnable) -> bool:
        """
        Attempts to remove a specific task from the thread pool queue.
        
        Only removes tasks that have not yet been executed. Tasks that are already running cannot be removed.
        Used when task cancellation is needed.
        
        Parameters
        ----------
        runnable : QRunnable
            Task to be removed from the queue
            
        Returns
        -------
        bool
            True: Task successfully removed from the queue
            False: Task could not be removed (already running or not found)
            
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidThreadPool, PyloidRunnable
        
        class Worker(PyloidRunnable):
            def run(self):
                print("Task executed")
                
        thread_pool = PyloidThreadPool()
        worker = Worker()
        
        # Add task
        thread_pool.start(worker)
        
        # Attempt to remove task
        if thread_pool.try_take(worker):
            print("Task removed from queue")
        else:
            print("Task could not be removed (already running or not found)")
        ```
        """
        return self.thread_pool.tryTake(runnable)

    def wait_for_done(self, timeout: Optional[int] = None) -> bool:
        """
        Waits for tasks to complete.
        
        If no timeout is specified, waits indefinitely until completion.
        
        Parameters
        ----------
        timeout : Optional[int]
            Wait time
            
        Returns
        -------
        bool
            True if tasks completed, False otherwise
            
        Examples
        --------
        ```python
        from pyloid.thread_pool import PyloidThreadPool
        
        thread_pool = PyloidThreadPool()
        thread_pool.wait_for_done()
        
        print("Tasks completed.")
        ```
        """
        if timeout is None:
            return self.thread_pool.waitForDone(-1)
        else:
            return self.thread_pool.waitForDone(timeout)