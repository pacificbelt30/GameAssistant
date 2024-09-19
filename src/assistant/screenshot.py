from typing import Tuple
import os
import pyautogui


def capture_screen(initial_point: Tuple[int, int]=(0, 0), width: int=600, height: int=600, base_dir: str='./data/', filename: str='screenshot.png') -> None:
    # 保存先を確認
    if os.path.exists(base_dir) and os.path.isfile(base_dir):
        raise FileExistsError(f'すでに {base_dir} ファイルが存在します')
    elif not os.path.isdir(base_dir):
        os.makedirs(base_dir)

    # 特定の領域をスクリーンショットとして撮影
    screenshot = pyautogui.screenshot(region=(*initial_point, width, height))
    screenshot.save(os.path.join(base_dir,filename))

