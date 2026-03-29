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
    empty_count = 0
    total_boxes = 0
    
    for i in range(fire_start, fire_end + 1):
        image_file = os.path.join(images_folder, f"{i}.jpg")
        
        if not os.path.exists(image_file):
            print(f"跳过（图片不存在）: {i}.jpg")
            continue
        
        # 检测火灾区域
        boxes = detect_fire_by_color(image_file)
        
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
                
                print(f"已处理: {i}.jpg ({len(boxes)} 个火灾区域）")
                success_count += 1
            else:
                # 没有检测到火灾区域，创建空文件
                print(f"警告: {i}.jpg 没有检测到火灾区域")
                empty_count += 1
    
    print()
    print(f"火灾照片处理完成！")
    print(f"  成功: {success_count}/{fire_end - fire_start + 1}")
    print(f"  无目标: {empty_count}")
    print(f"  总火灾区域: {total_boxes}")
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
    print("自动生成YOLO标签文件（火灾颜色检测）")
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