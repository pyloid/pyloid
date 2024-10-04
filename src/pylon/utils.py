import sys
import os


def get_resource_path(file_path):
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 경우
        return os.path.join(sys._MEIPASS, os.path.basename(file_path))
    else:
        # 일반 Python 스크립트로 실행되는 경우
        return file_path


def is_production():
    """
    현재 환경이 프로덕션 환경인지 확인하는 함수입니다.

    Returns:
        bool: 프로덕션 환경이면 True, 그렇지 않으면 False를 반환합니다.
    """
    return getattr(sys, 'frozen', False)
