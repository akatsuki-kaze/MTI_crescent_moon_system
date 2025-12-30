import cv2
import numpy as np

def denoise_image(self, image, method='median', **params):
        """
        对输入图像进行降噪处理
        
        参数:
            image: numpy.ndarray - 输入图像，可以是BGR格式(OpenCV默认)或RGB格式
            method: str - 降噪方法，可选值:
                'median' - 中值滤波(默认，适合椒盐噪声)
                'gaussian' - 高斯模糊(适合高斯噪声)
                'mean' - 均值滤波(简单平滑)
                'bilateral' - 双边滤波(保留边缘)
                'non_local_means' - 非局部均值滤波(效果好但速度慢)
            **params: 关键字参数，不同方法的具体参数:
                对于'median':
                    ksize: int - 滤波核大小，必须是奇数，默认3
                对于'gaussian':
                    ksize: tuple - 滤波核大小，默认(5,5)
                    sigma_x: float - X方向标准差，默认0
                    sigma_y: float - Y方向标准差，默认与sigma_x相同
                对于'mean':
                    ksize: tuple - 滤波核大小，默认(5,5)
                对于'bilateral':
                    d: int - 像素邻域直径，默认9
                    sigma_color: float - 颜色空间标准差，默认75
                    sigma_space: float - 坐标空间标准差，默认75
                对于'non_local_means':
                    h: float - 控制滤波强度，默认10
                    template_window_size: int - 模板窗口大小，必须是奇数，默认7
                    search_window_size: int - 搜索窗口大小，必须是奇数，默认21
        
        返回:
            numpy.ndarray - 降噪后的图像，与输入图像格式相同
        """
        # 确保输入是正确的图像格式
        if not isinstance(image, np.ndarray) or len(image.shape) not in (2, 3):
            raise ValueError("输入必须是灰度图像(2D数组)或彩色图像(3D数组)")
        
        # 保存输入图像的格式信息，用于后期转换
        is_rgb = False
        if len(image.shape) == 3 and image.shape[2] == 3:
            # 检查是否为RGB格式(通常由PIL等库加载)
            # 通过简单的统计判断，OpenCV默认BGR，通常蓝色通道值较低
            if image[:, :, 0].mean() > image[:, :, 2].mean():
                is_rgb = True
                # 转换为BGR以便OpenCV处理
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # 根据选择的方法进行降噪
        if method == 'median':
            ksize = params.get('ksize', 3)
            # 确保ksize是奇数
            if ksize % 2 == 0:
                ksize += 1
            result = cv2.medianBlur(image, ksize)
        
        elif method == 'gaussian':
            ksize = params.get('ksize', (5, 5))
            sigma_x = params.get('sigma_x', 0)
            sigma_y = params.get('sigma_y', sigma_x)
            result = cv2.GaussianBlur(image, ksize, sigma_x, sigma_y)
        
        elif method == 'mean':
            ksize = params.get('ksize', (5, 5))
            result = cv2.blur(image, ksize)
        
        elif method == 'bilateral':
            d = params.get('d', 9)
            sigma_color = params.get('sigma_color', 75)
            sigma_space = params.get('sigma_space', 75)
            result = cv2.bilateralFilter(image, d, sigma_color, sigma_space)
        
        elif method == 'non_local_means':
            # 非局部均值滤波对彩色图像需要特殊处理
            if len(image.shape) == 3:
                h = params.get('h', 10)
                template_window_size = params.get('template_window_size', 7)
                search_window_size = params.get('search_window_size', 21)
                # 确保窗口大小是奇数
                if template_window_size % 2 == 0:
                    template_window_size += 1
                if search_window_size % 2 == 0:
                    search_window_size += 1
                result = cv2.fastNlMeansDenoisingColored(
                    image, None, h, h, template_window_size, search_window_size
                )
            else:  # 灰度图像
                h = params.get('h', 10)
                template_window_size = params.get('template_window_size', 7)
                search_window_size = params.get('search_window_size', 21)
                if template_window_size % 2 == 0:
                    template_window_size += 1
                if search_window_size % 2 == 0:
                    search_window_size += 1
                result = cv2.fastNlMeansDenoising(
                    image, None, h, template_window_size, search_window_size
                )
        
        else:
            raise ValueError(f"不支持的降噪方法: {method}，可选方法: 'median', 'gaussian', 'mean', 'bilateral', 'non_local_means'")
        
        # 如果输入是RGB格式，转换回RGB
        if is_rgb:
            result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        
        return result

# waiting for update...
