import cv2
import numpy as np
import os

def detect_fire_by_color(image_path):
    """
    使用颜色检测火灾区域
    
    参数:
        image_path: 图片路径
    
    返回:
        boxes: 检测到的火灾区域列表 [(x1, y1, x2, y2), ...]
    """
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print(f"错误: 无法读取图片: {image_path}")
        return []
    
    # 转换为HSV颜色空间
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 定义火焰颜色的HSV范围
    # 火焰通常包含红色、橙色、黄色
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    
    lower_orange = np.array([10, 100, 100])
    upper_orange = np.array([25, 255, 255])
    
    lower_yellow = np.array([25, 100, 100])
    upper_yellow = np.array([35, 255, 255])
    
    # 创建掩码
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask3 = cv2.inRange(hsv, lower_orange, upper_orange)
    mask4 = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # 合并掩码
    mask = cv2.bitwise_or(mask1, mask2)
    mask = cv2.bitwise_or(mask, mask3)
    mask = cv2.bitwise_or(mask, mask4)
    
    # 形态学操作
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    boxes = []
    for contour in contours:
        # 计算轮廓面积
        area = cv2.contourArea(contour)
        
        # 过滤太小的区域
        if area < 100:
            continue
        
        # 获取边界框
        x, y, w, h = cv2.boundingRect(contour)
        
        # 过滤太小的框
        if w > 20 and h > 20:
            boxes.append((x, y, x + w, y + h))
    
    return boxes

def convert_to_yolo_format(box, img_width, img_height):
    """
    将边界框转换为YOLO格式
    
    参数:
        box: (x1, y1, x2, y2)
        img_width: 图片宽度
        img_height: 图片高度
    
    返回:
        (class_id, center_x, center_y, width, height)
    """
    x1, y1, x2, y2 = box
    
    # 计算中心点
    center_x = (x1 + x2) / 2.0 / img_width
    center_y = (y1 + y2) / 2.0 / img_height
    
    # 计算宽度和高度
    width = (x2 - x1) / img_width
    height = (y2 - y1) / img_height
    
    return (0, center_x, center_y, width, height)

def test_fire_detection(image_path):
    """
    测试火灾检测
    """
    print(f"测试图片: {image_path}")
    print()
    
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print(f"错误: 无法读取图片")
        return
    
    img_height, img_width = img.shape[:2]
    print(f"图片尺寸: {img_width}x{img_height}")
    print()
    
    # 检测火灾区域
    boxes = detect_fire_by_color(image_path)
    
    print(f"检测到 {len(boxes)} 个火灾区域")
    if len(boxes) > 0 and len(boxes) < 10:
        for i, box in enumerate(boxes[:5]):
            x1, y1, x2, y2 = box
            print(f"  {i+1}. 位置: ({x1}, {y1}) - ({x2}, {y2}), 尺寸: {x2-x1}x{y2-y1}")
    print()
    
    return boxes

def main():
    """
    主函数
    """
    print("="*60)
    print("火灾区域检测（颜色检测）")
    print("="*60)
    print()
    
    # 测试800.jpg图片
    image_path = 'datasets/bvn/images/train/800.jpg'
    
    if os.path.exists(image_path):
        boxes = test_fire_detection(image_path)
        
        print("="*60)
        print("检测完成！")
        print()
        
        if len(boxes) > 0:
            print(f"检测到 {len(boxes)} 个火灾区域")
            print("可以使用此方法生成标签文件")
        else:
            print("警告: 未检测到火灾区域")
            print("可能需要:")
            print("  1. 调整颜色范围")
            print("  2. 使用其他检测方法")
            print("  3. 手动标注")
    else:
        print(f"错误: 图片不存在: {image_path}")
    
    print()

if __name__ == '__main__':
    main()