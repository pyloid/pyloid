# from ..pyloid import Pyloid
# from ..api import PyloidAPI, Bridge
# from typing import Optional, Callable


# class EventAPI(PyloidAPI):
#     def __init__(self, window_id: str, app):
#         super().__init__()
#         self.window_id: str = window_id
#         self.app: PylonApp = app
#         self.subscribers = {}

#     @Bridge(str, Callable)
#     def on(self, event_name: str, callback: Callable):
#         """특정 이벤트를 구독합니다."""
#         if event_name not in self.subscribers:
#             self.subscribers[event_name] = []
#         self.subscribers[event_name].append(callback)

#     @Bridge(str, result=Optional[str])
#     def emit(self, event_name: str, *args, **kwargs):
#         """다른 윈도우로 특정 이벤트를 보냅니다."""
#         if event_name in self.subscribers:
#             for callback in self.subscribers[event_name]:
#                 callback(*args, **kwargs)
