import pygame
import numpy as np
import time
import serial
import serial.tools.list_ports
import sys
from collections import deque
running = True
joystick = None
check_funcs = {135,245,13,19}
#=========================================================

# 初始化Pygame和游戏手柄
pygame.init()
pygame.joystick.init()
def if_automode():
    # 检查手柄连接
    global joystick
    if pygame.joystick.get_count() == 0:
        print("未检测到手柄,请连接后重试！")
        return True
    else:
        # 初始化第一个手柄
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        return False

def check_if_joystick_connected():
    global joystick
    if joystick is None or not joystick.get_init():
        return False
    return True

def auto_connect_joystick(is_automode):
    global joystick
    if not is_automode:
        while True:
            if not check_if_joystick_connected():
                print("手柄断开，正在尝试重新连接...")
                pygame.joystick.quit()
                pygame.joystick.init()
                if pygame.joystick.get_count() > 0:
                    joystick = pygame.joystick.Joystick(0)
                    joystick.init()
                    print("手柄重新连接成功！")
            time.sleep(1)

# 摇杆参数
dead_zone = 0.01          # 死区过滤微小偏移
scale = 200               # 控制移动范围

# 扳机参数
LT_AXIS = 4               # 左扳机轴号(可能需要调整)
RT_AXIS = 5               # 右扳机轴号(可能需要调整)
lb_value = 0
if not if_automode():
    # 摇杆参数
    dead_zone = 0.01          # 死区过滤微小偏移
    scale = 200               # 控制移动范围

    # 扳机参数
    LT_AXIS = 4               # 左扳机轴号(可能需要调整)
    RT_AXIS = 5               # 右扳机轴号(可能需要调整)

    lb_value = (joystick.get_button(4))
#=========================================================
msg = ( 
        0#校验位
        ,127
        ,127
        ,127
        ,127#第四位
        ,0#第五位校验位
        ,0#第六位
        ,0#第七位
        ,0#第八位
        ,0#第九位X按键
        ,0#第位机械臂使能
        ,0#第十一位
        ,0#第十二位气缸
        ,0#第十三位
        ,190#第十四位校验位
        ,0#第十五位
        ,0#第十六位
        ,0
        ,0
        ,0#校验位
        )
msg = list(msg)

msg_get = (
        0#校验位
        ,0
        ,0
        ,0
        ,0#第四位
        ,0#第五位校验位
        ,0#第六位
        ,0#第七位
        ,0#第八位
        ,0#第九位
        ,0#第十位
        ,0#第十一位
        ,0#第十二位
        ,0#第十三位
        ,0#第十四位校验位
        ,0#第十五位
        ,0#第十六位
        ,0
        ,0
        ,0#校验位
)
msg_get = list(msg_get)
'''
Ubuntu下xinput与win略有差别，请前往手柄测试网页进行重新标号
Xbox 手柄
轴:
0: 左摇杆 X 轴(左:-1,右:1)
1: 左摇杆 Y 轴(上:-1,下:1)
2: 右摇杆 X 轴
3: 右摇杆 Y 轴
4: 左扳机(-1 到 1)
5: 右扳机(-1 到 1)
按键:
0: A
1: B
2: X
3: Y
4: 左肩部按钮(LB)
5: 右肩部按钮(RB)
6: 左扳机按钮(按下时触发)
7: 右扳机按钮(按下时触发)
8: 选择键(Back)
9: 开始键(Start)
10: 左摇杆按下
11: 右摇杆按下
方向键:
0: 十字方向键
PlayStation 手柄
轴:
0: 左摇杆 X 轴
1: 左摇杆 Y 轴
2: 右摇杆 X 轴
3: 右摇杆 Y 轴
按键:
0: X(方形)
1: O(圆形)
2: △(三角)
3: ▢(叉)
4: L1
5: R1
6: L2(按下时触发)
7: R2(按下时触发)
8: Share
9: Options
10: L3(左摇杆按下)
11: R3(右摇杆按下)
12: PlayStation 按钮
13: 触摸板按钮
方向键:
0: 十字方向键
'''
#=========================================================
class SerialCommunicator:
    def __init__(self):
        self.ser = None
        self.default_checksum_type = None  # 默认无校验

    def open(self, port, baudrate, bytesize=8, parity='N', stopbits=1):
        """打开串口
        :param port: 串口名称(如:COM3 或 /dev/ttyUSB0)
        :param baudrate: 波特率
        :param bytesize: 数据位(5-8),默认8
        :param parity: 校验位(N-无校验,E-偶校验,O-奇校验),默认N
        :param stopbits: 停止位(1, 1.5, 2),默认1
        """
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=0.1
            )
            return True
        except Exception as e:
            print(f"\r\033[031m打开串口失败:{e}\033[0m")
            return False
        
    def send(self):
        #self.ser.write(self.default_header)
        for  data_msg in msg:
            # 将整数转换为十六进制
            
            byte_data = bytes([data_msg])

            self.ser.write(byte_data)
            print(byte_data,end = '')
        print("",end="\r")
        #self.ser.write(self.default_footer)
        
    def read(self, size=20, check_values=None):
        """
        从串口读取数据，填充msg_get数组并校验预设校验位，返回对应结果
        :param size: 读取字节数（固定20，与msg_get长度匹配）
        :param check_values: 预设校验位字典，格式：{0: val0, 5: val5, 13: val13, 19: val19}，值为0-255的整数
        :return: 校验通过返回msg_get列表（元素为int型字节值）；校验失败返回原始bytes数据；
                参数错误/串口问题返回None
        """
        
        # 校验check_values参数合法性
        required_check_indices = {0, 5, 13, 19}  # 固定校验位位置
        if not check_values or not isinstance(check_values, dict):
            print("错误：check_values必须是包含校验位的字典")
            return False ,msg_get
        if set(check_values.keys()) != required_check_indices:
            print(f"错误：check_values必须包含键{required_check_indices}")
            return False ,msg_get
        for idx, val in check_values.items():
            if not isinstance(val, int) or not (0 <= val <= 255):
                print(f"错误：校验位{idx}的值必须是0-255的整数")
                return False ,msg_get
        
        # 检查串口状态
        if not (self.ser and self.ser.is_open):
            print("串口未打开")
            return False ,msg_get
        
        try:
            # 读取20字节完整数据（原始bytes）
            raw_data = b''
            while len(raw_data) < 20:
                remaining = 20 - len(raw_data)
                chunk = self.ser.read(remaining)  # 读取剩余所需字节
                if not chunk:  # 无数据（超时或断开）
                    print(f"警告：仅读取到{len(raw_data)}字节（需20字节）")
                    return False ,msg_get   # 返回错误
                raw_data += chunk
            
            # 校验所有预设校验位
            all_check_passed = True
            for idx in required_check_indices:
                if raw_data[idx] != check_values[idx]:
                    print(f"校验位{idx}不匹配：接收值={msg_get[idx]}, 预设值={check_values[idx]}")
                    all_check_passed = False

            # 根据校验结果返回对应数据
            if all_check_passed:
                print("所有校验位匹配，校验通过")
                # 将原始数据逐个字节写入msg_get（转换为int值）
                for i in range(20):
                    msg_get[i] = raw_data[i]  # raw_data[i]为单个字节，转为0-255的int
                return True , msg_get  # 返回填充后的数组
            else:
                print("校验失败，返回原始数据")
                return True , msg_get  # 返回0数据
        
        except Exception as e:
            print(f"读取数据异常：{e}")
            return None
        
    def close(self):
        """关闭串口"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None


def xy_collect(x, y,RIGHT_X,RIGHT_Y,scale,dead_zone,maxim,minim):
    """
    处理xy输入
    """
    x = int(mapping(x * scale, -scale, scale, maxim, minim))
    y = int(mapping(y * scale, -scale, scale, maxim, minim))
    RIGHT_X = int(mapping(RIGHT_X * scale, -scale, scale, maxim, minim))
    RIGHT_Y = int(mapping(RIGHT_Y * scale, -scale, scale, maxim, minim))

    # 处理死区
    if abs(x) < dead_zone * 660:
        x = 0
    if abs(y) < dead_zone * 660:
        y = 0
    if abs(RIGHT_X) < dead_zone * 660:
        RIGHT_X = 0
    if abs(RIGHT_Y) < dead_zone * 660:
        RIGHT_Y = 0

    return x, y , RIGHT_X , RIGHT_Y


def button_toggle():
    pygame.init()
    # 状态变量,0表示初始状态,1表示按下Y键后的状态
    state = 0
    # 记录Y键的上一次状态
    last_y_state = False
    # 事件队列,用于线程间通信
    event_queue = deque()
    # 线程停止标志
    running = True
    
    def read_joystick():
        nonlocal last_y_state, state
        try:
            while running:
                
                # 获取当前Y键状态(假设Y键为按钮3,具体取决于手柄映射)
                current_y_state = joystick.get_hat(0)[0]
                
                # 检测Y键是否从释放变为按下(上升沿触发)
                if current_y_state and not last_y_state:
                    state = 1 - state  # 切换状态:0->1 或 1->0
                    event_queue.append(state)
                
                # 更新上一次Y键状态
                last_y_state = current_y_state
                time.sleep(0.01)  # 避免CPU占用过高
        except Exception as e:
            print(f"读取手柄输入时出错: {e}")
    
    def process_events():
        try:
            while running:
                if event_queue:
                    current_state = event_queue.popleft()
                    msg[10] = current_state
                    print(f"输出: {current_state}")
                time.sleep(0.1)  # 降低处理频率
        except Exception as e:
            print(f"处理事件时出错: {e}")
    
    return read_joystick, process_events, running


#数值value从区间[a,b]映射到区间[c,d]
def mapping(value, a, b, c, d):
    original_range = np.array([a, b])
    target_range = np.array([c, d])
    mapped_value = np.interp(value, original_range, target_range)
    return mapped_value


def com_switch(com):
    """
    切换串口
    """
    ports_list = list(serial.tools.list_ports.comports())
    if len(ports_list) <= 0:
        print("无串口设备。")
    else:
        print("可用的串口设备如下:")
        for comport in ports_list:
            print(list(comport)[0], list(comport)[1])
    
    print("\033[33mswitch com{COM_PORTS}\033[0m".format(COM_PORTS=com))

    def clear_lines(num_lines):
        for _ in range(num_lines):
            sys.stdout.write("\033[F")  # 移动光标到上一行
            sys.stdout.write("\033[K")  # 清除整行内容

    key = (0, 0)
    set_com = 0

    while True:
        #事件遍历
        for event in pygame.event.get():
           key = joystick.get_hat(0)
           set_com = joystick.get_button(0)
           
        if key[1] == 1:
            com = com+1
            clear_lines(1)
            print("\033[33mswitch com{com}\033[0m".format(com=com))
        elif key[1] == -1:
            com = com-1
            clear_lines(1)
            print("\033[33mswitch com{com}\033[0m".format(com=com))
        elif key[0] == 1:
            com = com+5
            clear_lines(1)
            print("\033[33mswitch com{com}\033[0m".format(com=com))
        elif key[0] == -1:
            com = com-5
            clear_lines(1)
            print("\033[33mswitch com{com}\033[0m".format(com=com))
        else:
            if set_com == 1:
                clear_lines(1)
                print("\033[33mswitch com{com}\033[0m".format(com=com))
                return com
        time.sleep(0.1)

if __name__ == "__main__":
    print("测试message_process模块")