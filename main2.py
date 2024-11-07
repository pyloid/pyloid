from mss import mss

def get_screen_sources():
    with mss() as sct:
        # 모든 모니터 정보 가져오기
        monitors = sct.monitors[1:]  # 0번은 모든 모니터를 합친 전체 화면
        
        screens = []
        for i, monitor in enumerate(monitors):
            print(monitor)
            screen_info = {
                "id": f"screen_{i}",
                "name": f"Monitor {i+1}",
                "width": monitor["width"],
                "height": monitor["height"],
                "geometry": {
                    "x": monitor["left"],
                    "y": monitor["top"],
                    "width": monitor["width"],
                    "height": monitor["height"]
                }
            }
            screens.append(screen_info)
        
        return screens

print(get_screen_sources())
