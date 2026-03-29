import cv2
import numpy as np
import os

def detect_white_boxes(image_path):
    """
    检测图片中的白框
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法读取图片: {image_path}")
        return []
    
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 创建白色掩码（白色像素的值接近255）
    # 使用阈值检测白色区域
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # 查找轮廓
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    boxes = []
    for contour in contours:
        # 获取边界框
        x, y, w, h = cv2.boundingRect(contour)
        
        # 过滤掉太小的框
        if w > 10 and h > 10:
            boxes.append((x, y, w, h))
    
    return boxes, img.shape[:2]  # 返回框和图片尺寸(高度,宽度)

def convert_to_yolo_format(box, img_height, img_width):
    """
    将边界框转换为YOLO格式（归一化坐标）
    """
    x, y, w, h = box
    
    # 计算中心点坐标
    x_center = (x + w / 2) / img_width
    y_center = (y + h / 2) / img_height
    
    # 归一化宽度和高度
    width = w / img_width
    height = h / img_height
    
    return x_center, y_center, width, height

def process_single_image(image_path, output_path):
    """
    处理单张图片，生成YOLO格式标签文件
    """
    print(f"处理图片: {image_path}")
    
    # 检测白框
    boxes, (img_height, img_width) = detect_white_boxes(image_path)
    
    print(f"检测到 {len(boxes)} 个白框")
    print(f"图片尺寸: {img_width} x {img_height}")
    
    if not boxes:
        print("警告: 未检测到白框")
        return
    
    # 转换为YOLO格式并写入文件
    with open(output_path, 'w') as f:
        for i, box in enumerate(boxes):
            x, y, w, h = box
            print(f"  框 {i+1}: 原始坐标=({x}, {y}, {w}, {h})")
            
            # 转换为YOLO格式
            x_center, y_center, width, height = convert_to_yolo_format(box, img_height, img_width)
            
            # 写入文件，类别ID为0
            f.write(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            
            print(f"  框 {i+1}: YOLO格式=0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
    
    print(f"标签文件已保存到: {output_path}")

if __name__ == '__main__':
    # 处理1.jpg
    image_path = 'datasets/bvn/images/train/1.jpg'
    output_path = 'datasets/bvn/labels/train/1.txt'
    
    process_single_image(image_path, output_path)