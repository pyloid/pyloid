from PySide6.QtCore import QTimer, QObject, Qt

class PyloidTimer(QObject):
    def __init__(self):
        super().__init__()
        self.timers = {}

    def start_periodic_timer(self, interval, callback):
        """
        주기적으로 실행되는 타이머를 시작합니다.
        
        :param interval: 밀리초 단위의 간격
        :param callback: 실행할 콜백 함수
        :param auto_remove: 타이머 중지 시 자동 삭제 여부
        :return: 타이머 ID
        """
        return self._create_timer(interval, callback, single_shot=False, auto_remove=False)

    def start_single_shot_timer(self, delay, callback):
        """
        한 번만 실행되는 타이머를 시작합니다.
        
        :param delay: 밀리초 단위의 지연 시간
        :param callback: 실행할 콜백 함수
        :return: 타이머 ID
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
        지정된 ID의 타이머를 중지합니다.
        
        :param timer_id: 중지할 타이머의 ID
        """
        if timer_id in self.timers:
            self.timers[timer_id].stop()
            del self.timers[timer_id]

    def is_timer_active(self, timer_id):
        """
        지정된 ID의 타이머가 활성 상태인지 확인합니다.
        
        :param timer_id: 확인할 타이머의 ID
        :return: 타이머가 활성 상태이면 True, 그렇지 않으면 False
        """
        return timer_id in self.timers and self.timers[timer_id].isActive()

    def get_remaining_time(self, timer_id):
        """
        지정된 ID의 타이머의 남은 시간을 반환합니다.
        
        :param timer_id: 확인할 타이머의 ID
        :return: 남은 시간 (밀리초), 타이머가 없으면 None
        """
        if timer_id in self.timers:
            return self.timers[timer_id].remainingTime()
        return None

    def set_interval(self, timer_id, interval):
        """
        지정된 ID의 타이머의 간격을 설정합니다.
        
        :param timer_id: 설정할 타이머의 ID
        :param interval: 새로운 간격 (밀리초)
        """
        if timer_id in self.timers:
            self.timers[timer_id].setInterval(interval)

    def start_precise_periodic_timer(self, interval, callback):
        """
        정밀한 주기적 타이머를 시작합니다.
        
        :param interval: 밀리초 단위의 간격
        :param callback: 실행할 콜백 함수
        :return: 타이머 ID
        """
        return self._create_timer_with_type(interval, callback, Qt.TimerType.PreciseTimer)

    def start_coarse_periodic_timer(self, interval, callback):
        """
        덜 정밀한 주기적 타이머를 시작합니다.
        
        :param interval: 밀리초 단위의 간격
        :param callback: 실행할 콜백 함수
        :return: 타이머 ID
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
