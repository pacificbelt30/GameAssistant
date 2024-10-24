from typing import Tuple
import os
# import pyautogui
import requests
import json


def get_capture(initial_point: Tuple[int, int]=(0, 0), width: int=600, height: int=600):
    url = 'http://172.25.0.1:8000/capture'
    params = {'init_x': initial_point[0], 'init_y': initial_point[1], 'width': width, 'height': height}
    response = requests.get(url, params=params)
    return json.loads(response.text)
    
def capture_screen(initial_point: Tuple[int, int]=(0, 0), width: int=600, height: int=600, base_dir: str='./data/', filename: str='screenshot.png') -> None:
    # 保存先を確認
    if os.path.exists(base_dir) and os.path.isfile(base_dir):
        raise FileExistsError(f'すでに {base_dir} ファイルが存在します')
    elif not os.path.isdir(base_dir):
        os.makedirs(base_dir)

    # 特定の領域をスクリーンショットとして撮影
    screenshot = pyautogui.screenshot(region=(*initial_point, width, height))
    screenshot.save(os.path.join(base_dir,filename))

