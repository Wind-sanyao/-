import cv2
import numpy as np
import os

def detect_white_boxes_edge(image_path):
    """
    使用边缘检测检测图片中的白色矩形框（未填充）
    
    参数:
        image_path: 图片路径
    
    返回:
        boxes: 检测到的白框列表 [(x1, y1, x2, y2), ...]
    """
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print(f"错误: 无法读取图片: {image_path}")
        return []
    
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 创建白色掩码（白色像素）
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # 使用形态学操作连接边缘
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(binary, kernel, iterations=2)
    
    # 查找轮廓
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    boxes = []
    for contour in contours:
        # 获取轮廓的边界框
        x, y, w, h = cv2.boundingRect(contour)
        
        # 过滤太小的框（噪声）
        if w > 20 and h > 20:
            # 检查是否是矩形（长宽比合理）
            aspect_ratio = float(w) / h
            if 0.1 < aspect_ratio < 10:  # 排除过于细长的框
                boxes.append((x, y, x + w, y + h))
    
    return boxes

def detect_white_boxes_canny(image_path):
    """
    使用Canny边缘检测检测图片中的白色矩形框（未填充）
    
    参数:
        image_path: 图片路径
    
    返回:
        boxes: 检测到的白框列表 [(x1, y1, x2, y2), ...]
    """
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print(f"错误: 无法读取图片: {image_path}")
        return []
    
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 高斯模糊
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Canny边缘检测
    edges = cv2.Canny(blurred, 50, 150)
    
    # 查找轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    boxes = []
    for contour in contours:
        # 获取轮廓的边界框
        x, y, w, h = cv2.boundingRect(contour)
        
        # 过滤太小的框（噪声）
        if w > 20 and h > 20:
            # 检查是否是矩形（长宽比合理）
            aspect_ratio = float(w) / h
            if 0.1 < aspect_ratio < 10:  # 排除过于细长的框
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

def test_detection(image_path):
    """
    测试白框检测
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
    
    # 方法1: 边缘检测
    print("方法1: 边缘检测")
    boxes1 = detect_white_boxes_edge(image_path)
    print(f"  检测到 {len(boxes1)} 个白框")
    if len(boxes1) > 0 and len(boxes1) < 10:
        for i, box in enumerate(boxes1[:5]):
            x1, y1, x2, y2 = box
            print(f"    {i+1}. 位置: ({x1}, {y1}) - ({x2}, {y2}), 尺寸: {x2-x1}x{y2-y1}")
    print()
    
    # 方法2: Canny边缘检测
    print("方法2: Canny边缘检测")
    boxes2 = detect_white_boxes_canny(image_path)
    print(f"  检测到 {len(boxes2)} 个白框")
    if len(boxes2) > 0 and len(boxes2) < 10:
        for i, box in enumerate(boxes2[:5]):
            x1, y1, x2, y2 = box
            print(f"    {i+1}. 位置: ({x1}, {y1}) - ({x2}, {y2}), 尺寸: {x2-x1}x{y2-y1}")
    print()
    
    return boxes1, boxes2

def main():
    """
    主函数
    """
    print("="*60)
    print("白框检测测试")
    print("="*60)
    print()
    
    # 测试800.jpg图片
    image_path = 'datasets/bvn/images/train/800.jpg'
    
    if os.path.exists(image_path):
        boxes1, boxes2 = test_detection(image_path)
        
        print("="*60)
        print("检测完成！")
        print()
        
        # 选择最好的方法
        if len(boxes1) > 0 and len(boxes1) < 10:
            print("推荐使用方法1: 边缘检测")
        elif len(boxes2) > 0 and len(boxes2) < 10:
            print("推荐使用方法2: Canny边缘检测")
        else:
            print("警告: 两种方法都没有检测到合适的白框")
            print("可能需要调整参数")
    else:
        print(f"错误: 图片不存在: {image_path}")
    
    print()

if __name__ == '__main__':
    main()