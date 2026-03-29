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
    
    return boxes, img.shape[:2]

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

def process_single_image(image_path, output_path, verbose=False):
    """
    处理单张图片，生成YOLO格式标签文件
    """
    if verbose:
        print(f"处理图片: {image_path}")
    
    # 检测白框
    boxes, (img_height, img_width) = detect_white_boxes(image_path)
    
    if verbose:
        print(f"检测到 {len(boxes)} 个白框")
    
    if not boxes:
        if verbose:
            print("警告: 未检测到白框")
        # 创建空文件
        with open(output_path, 'w') as f:
            pass
        return False
    
    # 转换为YOLO格式并写入文件
    with open(output_path, 'w') as f:
        for box in boxes:
            x_center, y_center, width, height = convert_to_yolo_format(box, img_height, img_width)
            f.write(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
    
    return True

def process_all_images():
    """
    批量处理所有图片
    """
    base_dir = 'datasets/bvn'
    
    # 处理train和val文件夹
    for split in ['train', 'val']:
        images_dir = os.path.join(base_dir, 'images', split)
        labels_dir = os.path.join(base_dir, 'labels', split)
        
        if not os.path.exists(images_dir):
            print(f"警告: 图片目录不存在: {images_dir}")
            continue
        
        # 确保标签目录存在
        os.makedirs(labels_dir, exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"处理 {split} 集合")
        print(f"{'='*60}")
        
        # 获取所有图片文件
        image_files = [f for f in os.listdir(images_dir) if f.endswith('.jpg') or f.endswith('.png')]
        total = len(image_files)
        print(f"找到 {total} 张图片")
        
        success_count = 0
        empty_count = 0
        error_count = 0
        
        for i, filename in enumerate(image_files, 1):
            image_path = os.path.join(images_dir, filename)
            label_filename = filename.replace('.jpg', '.txt').replace('.png', '.txt')
            output_path = os.path.join(labels_dir, label_filename)
            
            try:
                result = process_single_image(image_path, output_path, verbose=False)
                
                if result:
                    success_count += 1
                else:
                    empty_count += 1
                
                # 显示进度
                if i % 100 == 0 or i == total:
                    print(f"进度: {i}/{total} ({i*100//total}%)")
                
            except Exception as e:
                error_count += 1
                print(f"错误处理 {filename}: {e}")
        
        print(f"\n{split} 集合处理完成:")
        print(f"  成功: {success_count} 张")
        print(f"  无目标: {empty_count} 张")
        print(f"  错误: {error_count} 张")
        print(f"  总计: {total} 张")

if __name__ == '__main__':
    process_all_images()