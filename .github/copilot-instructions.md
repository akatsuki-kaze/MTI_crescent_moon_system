# Copilot 使用指令（针对 MTI_crescent_moon_system）

目标：让 AI 编码助理快速理解本仓库的结构、约定与修改边界，以便进行安全、可预测的改动。

要点速览
- 本仓库分为三大模块：`basic_functional`（算法，如 PID）、`HAL`（硬件抽象与串口/手柄/鼠标交互）、`image_detection`（OpenCV 图像处理）。参见 [README.md](README.md).
- 串口协议为固定 20 字节帧（见 `HAL/message_process.py`），关键校验位索引集合为 {0,5,13,19}。修改通信结构时请保持帧长与校验逻辑一致。
- 控制值范围常用 0-255，中心/空档值为 127（见 `basic_functional/pid.py` 与 `HAL/message_process.py`），任何映射改动需同时更新发送与接收端处理。

重要文件（优先阅读）
- `README.md`：项目高层说明和三大目录职责。[README.md](README.md)
- `HAL/message_process.py`：手柄、串口封装与 20 字节消息格式示例（校验、send/read、`msg`/`msg_get` 数组）。[HAL/message_process.py](HAL/message_process.py)
- `HAL/pc_remote.py`：键盘/鼠标到遥控数组的映射例子（WSAD → 四位数组；鼠标中心偏移）。[HAL/pc_remote.py](HAL/pc_remote.py)
- `basic_functional/pid.py`：PID 输出映射到遥控器范围（返回 0-255，127 为中立）。[basic_functional/pid.py](basic_functional/pid.py)
- `image_detection/color_detect.py`：HSV 阈值与掩码生成示例，注意函数有 image_path / image 两种输入方式与直接显示窗口。 [image_detection/color_detect.py](image_detection/color_detect.py)

项目约定与注意事项
- 数据范围与映射：控制算法（PID、手柄映射）默认把中心定义为 127，向左/上为值增大或减小要根据调用方约定检查极性（例如 `pid.py` 中有对 current 取反）。修改时搜索 127 的含义。
- 串口交互：`SerialCommunicator.read()` 期望一次性读满 20 字节并校验索引位；若改为流式/可变长度帧，需在所有调用处同步调整并添加兼容层。
- 手柄/鼠标/键盘：代码同时使用 `pygame`（手柄）与 `pynput`/`pyautogui`（键鼠）。跨平台差异（Linux 下 Xlib）在 `HAL/pc_remote.py` 中有分支，请在修改前确认目标平台依赖。
- OpenCV 使用：`image_detection` 中函数会调用 `cv2.imshow()`，在无图形环境下运行会阻塞或错误。若用于 headless 推理，请替换显示调用并返回图像数组。

编辑/改动指南（具体示例）
- 若要调整 PID 范围：修改 `basic_functional/pid.py` 中映射和 `max_output`，并在 `HAL/message_process.py` 中验证发送 `msg` 的映射（`msg` 列表索引和含义）。
- 若要改变串口帧结构：先在 `HAL/message_process.py` 更新 `msg` / `msg_get` 定义，保持 `SerialCommunicator.read()` 的校验位逻辑或提供兼容读函数；接着查找所有使用 `SerialCommunicator` 的模块并更新调用。
- 若要添加新的图像处理流程：在 `image_detection/` 下增加模块并保证输出为二值掩码或坐标数组，调用方通常期望目标坐标（float）或掩码（ndarray）。避免直接在库函数中弹窗（`cv2.imshow`）以便于自动化测试。

依赖与运行提示
- 典型依赖：`numpy`, `opencv-python`, `pygame`, `pyserial`, `pynput`, `pyautogui`（Linux 可能需要 `python-xlib`）。
- 运行方式：仓库没有统一入口；通常在用户自建的 `main.py` 中按 README 所示导入模块，例如 `from HAL import depth_camera as cam` 并构建主循环。

对 AI 助理的具体行为期望
- 优先阅读并引用上述关键文件；任何修改须保留现有外部接口（函数签名与消息帧结构），除非同时更新并同步所有调用方。
- 修改串口、控制映射或图像阈值时，请在提交描述中列出受影响文件及理由，并提供简单的回归步骤（如何运行一个短脚本或手动验证）。
- 不要在没有测试或运行能力的情况下删除 `cv2.imshow` 或 UI 相关调用；改动时提供兼容替代（例如增加 `show=False` 参数）。

需要进一步澄清的点（请指明）
- 目标部署平台（Windows / Linux / Raspberry Pi）以确认图形与输入依赖。
- 是否希望把示例 `main.py` 补齐为仓库内可运行的演示入口？

---
如果你希望我把这写成更详尽的开发规范或生成示例 `main.py` 与 `requirements.txt`，告诉我目标平台并确认要我继续. 
