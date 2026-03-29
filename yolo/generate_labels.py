import cv2
import numpy as np
import os
from pathlib import Path

def detect_white_boxes(image_path, lower_white=np.array([200, 200, 200]), upper_white=np.array([255, 255, 255])):
    """
    检测图片中的白框
    
    参数:
        image_path: 图片路径
        lower_white: 白色下限（默认[200, 200, 200]）
        upper_white: 白色上限（默认[255, 255, 255]）
    
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
    
    # 创建白色掩码
    mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    boxes = []
    for contour in contours:
        # 获取轮廓的边界框
        x, y, w, h = cv2.boundingRect(contour)
        
        # 过滤太小的框（噪声）
        if w > 10 and h > 10:
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

def generate_labels_for_fire_images():
    """
    为火灾照片（800-1099）生成标签文件
    """
    print("="*60)
    print("处理火灾照片（800-1099）")
    print("="*60)
    print()
    
    # 图片和标签文件夹
    images_folder = 'datasets/bvn/images/train'
    labels_folder = 'datasets/bvn/labels/train'
    
    # 创建标签文件夹
    os.makedirs(labels_folder, exist_ok=True)
    
    # 处理火灾照片（800-1099）
    fire_start = 800
    fire_end = 1099
    
    success_count = 0
    total_boxes = 0
    
    for i in range(fire_start, fire_end + 1):
        image_file = os.path.join(images_folder, f"{i}.jpg")
        
        if not os.path.exists(image_file):
            print(f"跳过（图片不存在）: {i}.jpg")
            continue
        
        # 检测白框
        boxes = detect_white_boxes(image_file)
        
        # 读取图片尺寸
        img = cv2.imread(image_file)
        img_height, img_width = img.shape[:2]
        
        # 生成标签文件
        label_file = os.path.join(labels_folder, f"{i}.txt")
        
        with open(label_file, 'w') as f:
            if boxes:
                for box in boxes:
                    # 转换为YOLO格式
                    class_id, center_x, center_y, width, height = convert_to_yolo_format(box, img_width, img_height)
                    
                    # 写入标签
                    f.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
                    total_boxes += 1
                
                print(f"已处理: {i}.jpg ({len(boxes)} 个白框）")
            else:
                # 没有检测到白框，创建空文件
                print(f"警告: {i}.jpg 没有检测到白框")
        
        success_count += 1
    
    print()
    print(f"火灾照片处理完成！")
    print(f"  成功: {success_count}/{fire_end - fire_start + 1}")
    print(f"  总白框数: {total_boxes}")
    print()

def generate_labels_for_negative_samples():
    """
    为负样本（1100-1165）生成空标签文件
    """
    print("="*60)
    print("处理负样本（1100-1165）")
    print("="*60)
    print()
    
    # 图片和标签文件夹
    images_folder = 'datasets/bvn/images/train'
    labels_folder = 'datasets/bvn/labels/train'
    
    # 创建标签文件夹
    os.makedirs(labels_folder, exist_ok=True)
    
    # 处理负样本（1100-1165）
    negative_start = 1100
    negative_end = 1165
    
    success_count = 0
    
    for i in range(negative_start, negative_end + 1):
        image_file = os.path.join(images_folder, f"{i}.jpg")
        
        if not os.path.exists(image_file):
            print(f"跳过（图片不存在）: {i}.jpg")
            continue
        
        # 生成空的标签文件
        label_file = os.path.join(labels_folder, f"{i}.txt")
        
        with open(label_file, 'w') as f:
            pass  # 空文件表示没有目标
        
        success_count += 1
    
    print()
    print(f"负样本处理完成！")
    print(f"  成功: {success_count}/{negative_end - negative_start + 1}")
    print()

def main():
    """
    主函数
    """
    print("="*60)
    print("自动生成YOLO标签文件")
    print("="*60)
    print()
    
    # 处理火灾照片
    generate_labels_for_fire_images()
    
    # 处理负样本
    generate_labels_for_negative_samples()
    
    print("="*60)
    print("全部处理完成！")
    print()
    print("统计信息:")
    print("  火灾照片: 800-1099 (300张）")
    print("  负样本: 1100-1165 (66张）")
    print("  总计: 366张")
    print()
    print("标签文件已保存到: datasets/bvn/labels/train/")
    print()
    print("下一步:")
    print("  1. 检查标签文件是否正确")
    print("  2. 重新训练模型:")
    print("     python train_yolo.py")
    print("     或")
    print("     python train_yolo_v2.py (优化参数)")
    print()

if __name__ == '__main__':
    main()