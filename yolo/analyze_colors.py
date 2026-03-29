import cv2
import numpy as np
import os

def analyze_image_colors(image_path):
    """
    分析图片的颜色分布
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法读取图片: {image_path}")
        return
    
    print(f"分析图片: {image_path}")
    print(f"图片尺寸: {img.shape}")
    print()
    
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 统计灰度值分布
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    
    print("灰度值分布:")
    print("="*60)
    
    # 找出最常见的灰度值
    sorted_indices = np.argsort(hist.flatten())[::-1]
    
    print("最常见的10个灰度值:")
    for i in range(10):
        gray_value = sorted_indices[i]
        count = int(hist[gray_value][0])
        percentage = count / (img.shape[0] * img.shape[1]) * 100
        print(f"  灰度值 {gray_value}: {count} 像素 ({percentage:.2f}%)")
    
    print()
    
    # 统计白色像素（灰度值 > 200）
    white_pixels = np.sum(gray > 200)
    white_percentage = white_pixels / (img.shape[0] * img.shape[1]) * 100
    
    print(f"白色像素（灰度值 > 200）: {white_pixels} 像素 ({white_percentage:.2f}%)")
    
    # 统计浅色像素（灰度值 > 180）
    light_pixels = np.sum(gray > 180)
    light_percentage = light_pixels / (img.shape[0] * img.shape[1]) * 100
    
    print(f"浅色像素（灰度值 > 180）: {light_pixels} 像素 ({light_percentage:.2f}%)")
    
    # 统计浅色像素（灰度值 > 150）
    medium_light_pixels = np.sum(gray > 150)
    medium_light_percentage = medium_light_pixels / (img.shape[0] * img.shape[1]) * 100
    
    print(f"中浅色像素（灰度值 > 150）: {medium_light_pixels} 像素 ({medium_light_percentage:.2f}%)")
    
    print()
    
    # 尝试不同的阈值检测白框
    print("尝试不同阈值检测白框:")
    print("="*60)
    
    thresholds = [150, 180, 200, 220, 240]
    
    for threshold in thresholds:
        _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 10 and h > 10:
                boxes.append((x, y, w, h))
        
        print(f"阈值 {threshold}: 检测到 {len(boxes)} 个白框")
        
        if len(boxes) > 0 and len(boxes) < 20:
            print(f"  前3个白框:")
            for i, (x, y, w, h) in enumerate(boxes[:3]):
                print(f"    {i+1}. 位置: ({x}, {y}), 尺寸: {w}x{h}")
    
    print()

def main():
    """
    主函数
    """
    print("="*60)
    print("图片颜色分析工具")
    print("="*60)
    print()
    
    # 分析800.jpg图片
    image_path = 'datasets/bvn/images/train/800.jpg'
    
    if os.path.exists(image_path):
        analyze_image_colors(image_path)
    else:
        print(f"错误: 图片不存在: {image_path}")
    
    print()
    print("="*60)
    print("分析完成！")
    print()

if __name__ == '__main__':
    main()