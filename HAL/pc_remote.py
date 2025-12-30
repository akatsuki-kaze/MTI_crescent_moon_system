from pynput import keyboard
from pynput.mouse import Controller
import time
import threading
import platform

# ---------------------- 全局初始化（线程安全+跨平台） ----------------------
# 线程锁（保障按键数组更新安全）
key_lock = threading.Lock()

# 鼠标控制器（获取位置/移动鼠标）
mouse = Controller()

# 跨平台获取屏幕信息（中心位置+尺寸）
def get_screen_info():
    if platform.system() == "Linux":
        from Xlib import display
        d = display.Display()
        screen = d.screen()
        width, height = screen.width_in_pixels, screen.height_in_pixels
    else:
        import pyautogui
        width, height = pyautogui.size()
    center_x, center_y = width / 2, height / 2
    return center_x, center_y, width, height

center_x, center_y, screen_width, screen_height = get_screen_info()

# ---------------------- 1. WSAD按键功能配置 ----------------------
key_array = [127, 127, 127, 127]  # 四位数组：[上下, 左右, 预留, 预留]
pressed_keys = {'w': False, 's': False, 'a': False, 'd': False}

def update_key_array():
    """更新按键数组（WS/AD互斥处理）"""
    with key_lock:
        # 上下方向（W/S互斥）
        if pressed_keys['w'] and pressed_keys['s']:
            key_array[0] = 127
        elif pressed_keys['w']:
            key_array[0] = 255
        elif pressed_keys['s']:
            key_array[0] = 0
        else:
            key_array[0] = 127
        
        # 左右方向（A/D互斥）
        if pressed_keys['a'] and pressed_keys['d']:
            key_array[1] = 127
        elif pressed_keys['d']:
            key_array[1] = 255
        elif pressed_keys['a']:
            key_array[1] = 0
        else:
            key_array[1] = 127

def on_key_press(key):
    """按键按下回调"""
    try:
        key_char = key.char.lower()
        if key_char in pressed_keys:
            pressed_keys[key_char] = True
            update_key_array()
    except AttributeError:
        pass  # 忽略功能键

def on_key_release(key):
    """按键松开回调"""
    try:
        key_char = key.char.lower()
        if key_char in pressed_keys:
            pressed_keys[key_char] = False
            update_key_array()
    except AttributeError:
        pass
    # 按ESC键退出程序
    if key == keyboard.Key.esc:
        return False

# ---------------------- 2. 鼠标核心功能 ----------------------
def get_mouse_center_offset():
    """计算鼠标与屏幕中心的相对距离（dx, dy）"""
    current_x, current_y = mouse.position
    dx = current_x - center_x  # 正数=右侧，负数=左侧
    dy = current_y - center_y  # 正数=下方，负数=上方
    return (round(dx, 1), round(dy, 1))

def move_mouse_relative(dx, dy):
    """
    自定义鼠标相对移动函数（带边界保护）
    :param dx: X方向相对偏移（右=正，左=负）
    :param dy: Y方向相对偏移（下=正，上=负）
    :return: 移动后的绝对位置（x, y）
    """
    current_x, current_y = mouse.position
    target_x = current_x + dx
    target_y = current_y + dy
    # 限制鼠标在屏幕内
    target_x = max(0, min(target_x, screen_width - 1))
    target_y = max(0, min(target_y, screen_height - 1))
    mouse.position = (target_x, target_y)
    return (round(target_x, 1), round(target_y, 1))

# ---------------------- 主程序（实时输出+功能演示） ----------------------
def main():
    # 启动键盘监听器（异步线程）
    key_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    key_listener.start()

    print("=" * 80)
    print(f"屏幕信息：{screen_width}×{screen_height} 像素 | 中心位置：({center_x:.1f}, {center_y:.1f})")
    print("功能说明：")
    print("1. WSAD按键控制四位数组：[上下(W=255/S=0), 左右(D=255/A=0), 127, 127]（同时按对应位=127）")
    print("2. 实时输出鼠标与中心的相对距离（dx, dy）")
    print("3. 调用 move_mouse_relative(dx, dy) 实现鼠标相对移动")
    print("4. 按 ESC 键退出程序")
    print("=" * 80)

    # 可选：测试自定义鼠标移动（取消注释即可）
    # print("\n测试：鼠标相对当前位置右移100像素、上移50像素")
    # new_pos = move_mouse_relative(100, -50)
    # print(f"移动后鼠标位置：{new_pos}")
    # time.sleep(1)

    try:
        # 实时输出（10Hz刷新，不刷屏）
        while key_listener.is_alive():
            # 读取按键数组（线程安全）
            with key_lock:
                current_keys = key_array.copy()
            # 读取鼠标相对距离
            mouse_offset = get_mouse_center_offset()

            # 格式化输出（清晰显示两项核心数据）
            print(f"\r按键数组：{current_keys} | 鼠标-中心相对距离：dx={mouse_offset[0]:6.1f}px, dy={mouse_offset[1]:6.1f}px", end="")
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        # 优雅退出
        key_listener.stop()
        key_listener.join()
        print("\n\n程序已退出！")

if __name__ == "__main__":
    main()