import pyrealsense2 as rs
import numpy as np
import cv2

class RealSenseCamera:
    def __init__(self):
        # 配置深度和颜色流
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        
        # 配置流的分辨率和格式
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 60)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)
        
        # 启动流
        self.profile = self.pipeline.start(self.config)
        
        # 获取深度传感器的深度标尺
        self.depth_sensor = self.profile.get_device().first_depth_sensor()
        self.depth_scale = self.depth_sensor.get_depth_scale()
        
        # 创建对齐对象（将深度框与彩色框对齐）
        self.align_to = rs.stream.color
        self.align = rs.align(self.align_to)
        
        # 获取内参
        self.intrinsics = None
        
    def get_rgb_frame(self):
        """获取彩色图像帧"""
        # 等待一对连贯的帧
        frames = self.pipeline.wait_for_frames()
        
        # 对齐深度帧与颜色帧
        aligned_frames = self.align.process(frames)
        
        # 获取颜色帧
        color_frame = aligned_frames.get_color_frame()
        
        if not color_frame:
            return None

        # 保存内参（首次调用时）
        if self.intrinsics is None:
            self.intrinsics = color_frame.profile.as_video_stream_profile().intrinsics
            
        # 转换为numpy数组并返回
        return np.asanyarray(color_frame.get_data())
    
    def get_depth_frame(self, min_depth=0.1, max_depth=5.0):
        """
        获取深度图像帧，并只显示指定深度范围内的内容
        
        参数:
            min_depth: 最小深度值（米）
            max_depth: 最大深度值（米）
            
        返回:
            彩色映射的深度图像
        """
        # 等待一对连贯的帧
        frames = self.pipeline.wait_for_frames()
        
        # 对齐深度帧与颜色帧
        aligned_frames = self.align.process(frames)
        
        # 获取对齐的深度帧
        aligned_depth_frame = aligned_frames.get_depth_frame()
        
        if not aligned_depth_frame:
            return None
        
        # 转换为numpy数组
        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        
        # 将深度值转换为米
        depth_in_meters = depth_image * self.depth_scale
        
        # 创建掩码，只保留指定深度范围内的像素
        mask = (depth_in_meters >= min_depth) & (depth_in_meters <= max_depth)
        depth_image_masked = depth_image.copy()
        depth_image_masked[~mask] = 0
        
        # 深度图像的可视化
        depth_colormap = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_image_masked, alpha=0.03), 
            cv2.COLORMAP_JET
        )
        
        return depth_colormap
    
    def get_distance(self, x, y):
        """
        获取指定像素点的三维坐标和距离
        
        参数:
            x: 像素点的x坐标
            y: 像素点的y坐标
            
        返回:
            包含三维坐标和距离的字典，或None（如果获取失败）
        """
        # 等待一对连贯的帧
        frames = self.pipeline.wait_for_frames()
        
        # 对齐深度帧与颜色帧
        aligned_frames = self.align.process(frames)
        
        # 获取对齐的深度帧和颜色帧
        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        
        if not aligned_depth_frame or not color_frame:
            return None
            
        # 保存内参（首次调用时）
        if self.intrinsics is None:
            self.intrinsics = color_frame.profile.as_video_stream_profile().intrinsics
        
        # 检查坐标是否在有效范围内
        color_image = np.asanyarray(color_frame.get_data())
        if x < 0 or x >= color_image.shape[1] or y < 0 or y >= color_image.shape[0]:
            print("像素坐标超出图像范围")
            return None
        
        # 获取深度值（米）
        depth = aligned_depth_frame.get_distance(x, y)
        
        if depth <= 0:
            print("无法获取有效深度值")
            return None
        
        # 将像素坐标转换为三维坐标
        depth_point = rs.rs2_deproject_pixel_to_point(self.intrinsics, [x, y], depth)
        x3d, y3d, z3d = depth_point
        
        return {
            'x': x3d,
            'y': y3d,
            'z': z3d,
            'distance': depth  # z坐标与距离在这个场景下是相同的
        }
    
    def stop(self):
        """停止相机流并释放资源"""
        self.pipeline.stop()


if __name__ == "__main__":
    d415 = RealSenseCamera()
    try:
        while True:
            frame = d415.get_rgb_frame()
            if frame is not None:
                # 打印帧尺寸（正常应为 (480, 640, 3)）
                print(f"帧尺寸: {frame.shape}")
                # 打印左上角10x10区域的像素值（全黑则大部分为0）
                print(f"像素示例: {frame[:10, :10, :]}")
                cv2.imshow('RGB 图像', frame)
            else:
                print("未获取到帧")
            
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
    finally:
        rs.stop()
        cv2.destroyAllWindows()