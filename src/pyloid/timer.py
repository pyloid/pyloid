from PySide6.QtCore import QTimer, QObject, Qt

class PyloidTimer(QObject):
    def __init__(self):
        """
        Constructor for the PyloidTimer class.

        This class is based on PySide6's QTimer and allows for easy creation and management of various types of timers.
        """
        super().__init__()
        self.timers = {}

    def start_periodic_timer(self, interval, callback):
        """
        Starts a periodic timer.

        This function starts a timer that repeatedly executes the callback function at the given interval.

        Parameters
        ----------
        interval : int
            Interval in milliseconds
        callback : function
            Callback function to execute

        Returns
        -------
        int
            Timer ID

        Example
        -------
        ```python
        from pyloid.timer import PyloidTimer

        timer_manager = PyloidTimer()

        def print_hello():
            print("Hello!")

        # Start a timer that prints "Hello!" every 2 seconds
        timer_id = timer_manager.start_periodic_timer(2000, print_hello)
        ```
        """
        return self._create_timer(interval, callback, single_shot=False, auto_remove=False)

    def start_single_shot_timer(self, delay, callback):
        """
        Starts a single-shot timer.

        This function starts a timer that executes the callback function once after the given delay.

        Parameters
        ----------
        delay : int
            Delay in milliseconds
        callback : function
            Callback function to execute

        Returns
        -------
        int
            Timer ID

        Example
        -------
        ```python
        from pyloid.timer import PyloidTimer

        timer_manager = PyloidTimer()

        def delayed_message():
            print("5 seconds have passed!")

        # Start a single-shot timer that prints a message after 5 seconds
        timer_id = timer_manager.start_single_shot_timer(5000, delayed_message)
        ```
        """
        return self._create_timer(delay, callback, single_shot=True, auto_remove=True)

    def _create_timer(self, interval, callback, single_shot=False, auto_remove=False):
        timer = QTimer(self)
        timer.setInterval(interval)
        timer.setSingleShot(single_shot)
        
        if auto_remove or single_shot:
            timer.timeout.connect(lambda: self._timer_finished(callback, id(timer)))
        else:
            timer.timeout.connect(callback)
        
        timer.start()
        
        timer_id = id(timer)
        self.timers[timer_id] = timer
        return timer_id

    def _timer_finished(self, callback, timer_id):
        callback()
        self.stop_timer(timer_id)

    def stop_timer(self, timer_id):
        """
        Stops the timer with the specified ID.

        This function stops the timer corresponding to the given timer ID and removes it from the timer list.

        Parameters
        ----------
        timer_id : int
            ID of the timer to stop

        Example
        -------
        ```python
        from pyloid.timer import PyloidTimer

        timer_manager = PyloidTimer()

        # Stop the timer using its ID
        timer_manager.stop_timer(timer_id)
        ```
        """
        if timer_id in self.timers:
            self.timers[timer_id].stop()
            del self.timers[timer_id]

    def is_timer_active(self, timer_id):
        """
        Checks if the timer with the specified ID is active.

        This function returns whether the timer corresponding to the given timer ID is currently active.

        Parameters
        ----------
        timer_id : int
            ID of the timer to check

        Returns
        -------
        bool
            True if the timer is active, False otherwise

        Example
        -------
        ```python
        from pyloid.timer import PyloidTimer

        timer_manager = PyloidTimer()

        if timer_manager.is_timer_active(timer_id):
            print("The timer is still running.")
        else:
            print("The timer has stopped.")
        ```
        """
        return timer_id in self.timers and self.timers[timer_id].isActive()

    def get_remaining_time(self, timer_id):
        """
        Returns the remaining time of the timer with the specified ID.

        This function returns the remaining time of the timer corresponding to the given timer ID in milliseconds.

        Parameters
        ----------
        timer_id : int
            ID of the timer to check

        Returns
        -------
        int or None
            Remaining time in milliseconds, or None if the timer does not exist

        Example
        -------
        ```python
        from pyloid.timer import PyloidTimer

        timer_manager = PyloidTimer()

        remaining_time = timer_manager.get_remaining_time(timer_id)
        if remaining_time is not None:
            print(f"{remaining_time}ms remaining.")
        ```
        """
        if timer_id in self.timers:
            return self.timers[timer_id].remainingTime()
        return None

    def set_interval(self, timer_id, interval):
        """
        Sets the interval of the timer with the specified ID.

        This function sets a new interval for the timer corresponding to the given timer ID.

        Parameters
        ----------
        timer_id : int
            ID of the timer to set
        interval : int
            New interval in milliseconds

        Example
        -------
        ```python
        from pyloid.timer import PyloidTimer

        timer_manager = PyloidTimer()

        # Change the timer interval to 3 seconds
        timer_manager.set_interval(timer_id, 3000)
        ```
        """
        if timer_id in self.timers:
            self.timers[timer_id].setInterval(interval)

    def start_precise_periodic_timer(self, interval, callback):
        """
        Starts a precise periodic timer.

        This function starts a timer that repeatedly executes the callback function at precise intervals.
        
        Note
        ----
        Precise timers consume more CPU resources.

        Parameters
        ----------
        interval : int
            Interval in milliseconds
        callback : function
            Callback function to execute

        Returns
        -------
        int
            Timer ID

        Example
        -------
        ```python
        from pyloid.timer import PyloidTimer

        timer_manager = PyloidTimer()

        def precise_task():
            print("Executing precise task")

        # Start a precise periodic timer with a 100ms interval
        precise_timer_id = timer_manager.start_precise_periodic_timer(100, precise_task)
        ```
        """
        return self._create_timer_with_type(interval, callback, Qt.TimerType.PreciseTimer)

    def start_coarse_periodic_timer(self, interval, callback):
        """
        Starts a coarse periodic timer.

        This function starts a timer that repeatedly executes the callback function at coarse intervals.

        Note
        ----
        Coarse timers consume less CPU resources.

        Parameters
        ----------
        interval : int
            Interval in milliseconds
        callback : function
            Callback function to execute

        Returns
        -------
        int
            Timer ID

        Example
        -------
        ```python
        from pyloid.timer import PyloidTimer

        timer_manager = PyloidTimer()

        def coarse_task():
            print("Executing coarse task")

        # Start a coarse periodic timer with a 500ms interval
        coarse_timer_id = timer_manager.start_coarse_periodic_timer(500, coarse_task)
        ```
        """
        return self._create_timer_with_type(interval, callback, Qt.TimerType.CoarseTimer)

    def _create_timer_with_type(self, interval, callback, timer_type, auto_remove=False):
        timer = QTimer(self)
        timer.setInterval(interval)
        timer.setTimerType(timer_type)
        
        if auto_remove:
            timer.timeout.connect(lambda: self._timer_finished(callback, id(timer)))
        else:
            timer.timeout.connect(callback)
        
        timer.start()
        
        timer_id = id(timer)
        self.timers[timer_id] = timer
        return timer_id
