import cv2
import numpy as np

def extract_red_regions(image_path=None, image=None):
        """
        提取图像中的红色部分并返回二值化图像
        
        参数:
            image_path: 图像文件路径，如果提供则从路径加载图像
            image: 已加载的图像，如果提供则直接使用
            
        返回:
            二值化图像，红色区域
        """
        # 确保至少提供了一个图像源
        if image_path is None and image is None:
            print("错误：必须提供image_path或image参数")
            return None
        
        # 加载图像（如果提供了路径）
        try:
            if image_path is not None:
                image = cv2.imread(image_path)
                if image is None:
                    print(f"错误：无法从路径 {image_path} 加载图像")
                    return None
        except Exception as e:
            print(f"加载图像时发生错误：{str(e)}")
            return None
        
        # 将BGR图像转换为HSV颜色空间，HSV更适合颜色检测
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 定义HSV中红色的范围（红色在HSV中有两个范围）
        # 较低的红色范围
        lower_red1 = np.array([0, 100, 70])
        upper_red1 = np.array([6, 240, 240])
        
        # 较高的红色范围
        lower_red2 = np.array([174, 80, 110])
        upper_red2 = np.array([180, 240, 240])
        
        # 根据阈值范围创建掩码
        mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
        
        # 合并两个掩码，得到完整的红色区域掩码
        red_mask = mask1 + mask2
        
        # 反光区域掩码
        refl_mask = cv2.inRange(hsv_image, np.array([0, 0, 220]), np.array([180, 80, 255]))
        # 合并红色掩码和反光掩码
        combined_mask = cv2.bitwise_or(red_mask, refl_mask)
        
        # 对掩码进行一些形态学操作，去除噪声并填充空洞
        kernel = np.ones((5, 5), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        cv2.imshow("Red_Mask", combined_mask)
        return combined_mask

def extract_blue_regions(image_path=None, image=None):
    """
    提取图像中的蓝色部分并返回二值化图像
    
    参数:
        image_path: 图像文件路径，如果提供则从路径加载图像
        image: 已加载的图像，如果提供则直接使用
        
    返回:
        二值化图像，蓝色区域
    """
    # 确保至少提供了一个图像源
    if image_path is None and image is None:
        print("错误：必须提供image_path或image参数")
        return None
    
    # 加载图像（如果提供了路径）
    try:
        if image_path is not None:
            image = cv2.imread(image_path)
            if image is None:
                print(f"错误：无法从路径 {image_path} 加载图像")
                return None
    except Exception as e:
        print(f"加载图像时发生错误：{str(e)}")
        return None
    
    # 将BGR图像转换为HSV颜色空间，HSV更适合颜色检测
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # 定义HSV中蓝色的范围（蓝色为连续范围）
    # 可根据实际场景调整阈值（H:100-130左右，S和V根据亮度调整）
    lower_blue = np.array([100, 50, 50])    # 较低的蓝色范围
    upper_blue = np.array([130, 255, 255])  # 较高的蓝色范围
    
    # 根据阈值范围创建蓝色掩码
    blue_mask = cv2.inRange(hsv_image, lower_blue, upper_blue)
    
    # 反光区域掩码（高亮度、低饱和度区域，适用于蓝色反光）
    refl_mask = cv2.inRange(hsv_image, np.array([0, 0, 220]), np.array([180, 80, 255]))
    # 合并蓝色掩码和反光掩码
    combined_mask = cv2.bitwise_or(blue_mask, refl_mask)
    
    # 形态学操作：去除噪声并填充空洞
    kernel = np.ones((5, 5), np.uint8)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)  # 填充空洞
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)   # 去除噪声
    cv2.imshow("Blue_Mask", combined_mask)  # 窗口名同步修改
    return combined_mask

def red_regions_minus_edges(self, image_path=None, image=None):
    """
    提取红色区域并减去边缘检测结果

    参数:
        image_path: 图像文件路径，如果提供则从路径加载图像
        image: 已加载的图像，如果提供则直接使用
        
    返回:
        处理后的二值化图像，红色区域减去边缘
    """
    # 确保至少提供了一个图像源
    if image_path is None and image is None:
        print("错误：必须提供image_path或image参数")
        return None

    # 加载图像（如果提供了路径）
    try:
        if image_path is not None:
            original_image = cv2.imread(image_path)
            if original_image is None:
                print(f"错误：无法从路径 {image_path} 加载图像")
                return None
        else:
            original_image = image.copy()
    except Exception as e:
        print(f"加载图像时发生错误：{str(e)}")
        return None

    # 提取红色区域
    red_regions = self.extract_red_regions(image=original_image)

    # 进行边缘检测
    edges = self.process_image(original_image)

    # 从红色区域中减去边缘（使用位运算NOT和AND）
    # 首先创建边缘的反掩码
    edges_inv = cv2.bitwise_not(edges)
    # 然后将红色区域与边缘的反掩码进行AND运算
    result = cv2.bitwise_and(red_regions, edges_inv)

    return result

#waiting for update...