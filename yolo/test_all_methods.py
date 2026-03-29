import cv2
import numpy as np
import os

def detect_white_boxes_hough(image_path):
    """
    使用霍夫变换检测图片中的白色矩形框（未填充）
    
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
    
    # 创建白色掩码
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # 反转（白色变成黑色，黑色变成白色）
    inverted = cv2.bitwise_not(binary)
    
    # 使用形态学操作连接边缘
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(inverted, kernel, iterations=1)
    
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

def detect_white_boxes_contour(image_path):
    """
    使用轮廓检测检测图片中的白色矩形框（未填充）
    
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
    
    # 创建白色掩码（使用较低的阈值）
    _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    
    # 查找轮廓
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    boxes = []
    for contour in contours:
        # 计算轮廓面积
        area = cv2.contourArea(contour)
        
        # 过滤太小的轮廓
        if area < 100:
            continue
        
        # 获取轮廓的边界框
        x, y, w, h = cv2.boundingRect(contour)
        
        # 过滤太小的框（噪声）
        if w > 20 and h > 20:
            # 检查是否是矩形（长宽比合理）
            aspect_ratio = float(w) / h
            if 0.1 < aspect_ratio < 10:  # 排除过于细长的框
                boxes.append((x, y, x + w, y + h))
    
    return boxes

def detect_white_boxes_adaptive(image_path):
    """
    使用自适应阈值检测图片中的白色矩形框（未填充）
    
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
    
    # 使用自适应阈值
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    # 反转
    inverted = cv2.bitwise_not(adaptive)
    
    # 查找轮廓
    contours, _ = cv2.findContours(inverted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    boxes = []
    for contour in contours:
        # 计算轮廓面积
        area = cv2.contourArea(contour)
        
        # 过滤太小的轮廓
        if area < 100:
            continue
        
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

def test_all_methods(image_path):
    """
    测试所有白框检测方法
    """
    print(f"测试图片: {image_path}")
    print()
    
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print(f"错误: 无法读取图片")
        return None
    
    img_height, img_width = img.shape[:2]
    print(f"图片尺寸: {img_width}x{img_height}")
    print()
    
    # 方法1: 霍夫变换
    print("方法1: 霍夫变换")
    boxes1 = detect_white_boxes_hough(image_path)
    print(f"  检测到 {len(boxes1)} 个白框")
    if len(boxes1) > 0 and len(boxes1) < 10:
        for i, box in enumerate(boxes1[:5]):
            x1, y1, x2, y2 = box
            print(f"    {i+1}. 位置: ({x1}, {y1}) - ({x2}, {y2}), 尺寸: {x2-x1}x{y2-y1}")
    print()
    
    # 方法2: 轮廓检测
    print("方法2: 轮廓检测")
    boxes2 = detect_white_boxes_contour(image_path)
    print(f"  检测到 {len(boxes2)} 个白框")
    if len(boxes2) > 0 and len(boxes2) < 10:
        for i, box in enumerate(boxes2[:5]):
            x1, y1, x2, y2 = box
            print(f"    {i+1}. 位置: ({x1}, {y1}) - ({x2}, {y2}), 尺寸: {x2-x1}x{y2-y1}")
    print()
    
    # 方法3: 自适应阈值
    print("方法3: 自适应阈值")
    boxes3 = detect_white_boxes_adaptive(image_path)
    print(f"  检测到 {len(boxes3)} 个白框")
    if len(boxes3) > 0 and len(boxes3) < 10:
        for i, box in enumerate(boxes3[:5]):
            x1, y1, x2, y2 = box
            print(f"    {i+1}. 位置: ({x1}, {y1}) - ({x2}, {y2}), 尺寸: {x2-x1}x{y2-y1}")
    print()
    
    # 选择最好的方法
    best_method = None
    best_boxes = None
    
    for method_name, boxes in [("霍夫变换", boxes1), ("轮廓检测", boxes2), ("自适应阈值", boxes3)]:
        if 0 < len(boxes) < 10:
            best_method = method_name
            best_boxes = boxes
            break
    
    return best_method, best_boxes

def main():
    """
    主函数
    """
    print("="*60)
    print("白框检测测试（多种方法）")
    print("="*60)
    print()
    
    # 测试800.jpg图片
    image_path = 'datasets/bvn/images/train/800.jpg'
    
    if os.path.exists(image_path):
        best_method, best_boxes = test_all_methods(image_path)
        
        print("="*60)
        print("检测完成！")
        print()
        
        if best_method:
            print(f"推荐使用方法: {best_method}")
            print(f"检测到 {len(best_boxes)} 个白框")
        else:
            print("警告: 所有方法都没有检测到合适的白框")
            print("可能需要:")
            print("  1. 手动标注")
            print("  2. 调整检测参数")
            print("  3. 检查图片是否真的有白框")
    else:
        print(f"错误: 图片不存在: {image_path}")
    
    print()

if __name__ == '__main__':
    main()