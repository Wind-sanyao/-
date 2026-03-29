import cv2
import numpy as np
import os

def detect_white_boxes_lines(image_path):
    """
    使用霍夫直线检测检测图片中的白色矩形框（未填充）
    
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
    
    # Canny边缘检测
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # 霍夫直线检测
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100, 
                           minLineLength=50, maxLineGap=10)
    
    if lines is None:
        return []
    
    # 绘制直线
    line_img = np.zeros_like(img)
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(line_img, (x1, y1), (x2, y2), (255, 255, 255), 2)
    
    # 查找轮廓
    gray_lines = cv2.cvtColor(line_img, cv2.COLOR_BGR2GRAY)
    contours, _ = cv2.findContours(gray_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
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

def detect_white_boxes_color(image_path):
    """
    使用颜色检测检测图片中的白色矩形框（未填充）
    
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
    
    # 转换为HSV颜色空间
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 定义白色的HSV范围
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    
    # 创建白色掩码
    mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
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

def test_new_methods(image_path):
    """
    测试新的白框检测方法
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
    
    # 方法1: 霍夫直线检测
    print("方法1: 霍夫直线检测")
    boxes1 = detect_white_boxes_lines(image_path)
    print(f"  检测到 {len(boxes1)} 个白框")
    if len(boxes1) > 0 and len(boxes1) < 10:
        for i, box in enumerate(boxes1[:5]):
            x1, y1, x2, y2 = box
            print(f"    {i+1}. 位置: ({x1}, {y1}) - ({x2}, {y2}), 尺寸: {x2-x1}x{y2-y1}")
    print()
    
    # 方法2: 颜色检测
    print("方法2: 颜色检测（HSV）")
    boxes2 = detect_white_boxes_color(image_path)
    print(f"  检测到 {len(boxes2)} 个白框")
    if len(boxes2) > 0 and len(boxes2) < 10:
        for i, box in enumerate(boxes2[:5]):
            x1, y1, x2, y2 = box
            print(f"    {i+1}. 位置: ({x1}, {y1}) - ({x2}, {y2}), 尺寸: {x2-x1}x{y2-y1}")
    print()
    
    # 选择最好的方法
    best_method = None
    best_boxes = None
    
    for method_name, boxes in [("霍夫直线检测", boxes1), ("颜色检测", boxes2)]:
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
    print("白框检测测试（新方法）")
    print("="*60)
    print()
    
    # 测试800.jpg图片
    image_path = 'datasets/bvn/images/train/800.jpg'
    
    if os.path.exists(image_path):
        best_method, best_boxes = test_new_methods(image_path)
        
        print("="*60)
        print("检测完成！")
        print()
        
        if best_method:
            print(f"推荐使用方法: {best_method}")
            print(f"检测到 {len(best_boxes)} 个白框")
        else:
            print("警告: 所有方法都没有检测到合适的白框")
            print()
            print("可能的原因:")
            print("  1. 白框太细，边缘检测不到")
            print("  2. 白框颜色不是纯白色")
            print("  3. 白框样式不同（不是矩形边框）")
            print()
            print("建议:")
            print("  1. 手动查看图片，确认白框情况")
            print("  2. 使用标注工具手动标注")
            print("  3. 调整检测参数")
    else:
        print(f"错误: 图片不存在: {image_path}")
    
    print()

if __name__ == '__main__':
    main()