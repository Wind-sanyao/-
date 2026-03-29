from ultralytics import YOLO
import os
from pathlib import Path

def detect_fire_in_images(image_folder, model_path='runs/detect_v2/weights/best.pt', conf_threshold=0.25):
    """
    使用训练好的模型检测图片中的火灾
    
    参数:
        image_folder: 图片文件夹
        model_path: 模型路径
        conf_threshold: 置信度阈值（默认0.25）
    """
    print("="*60)
    print("火灾检测")
    print("="*60)
    print()
    
    # 加载模型
    print(f"加载模型: {model_path}")
    model = YOLO(model_path)
    
    # 获取图片文件夹中的所有图片
    image_folder = Path(image_folder)
    image_files = []
    
    # 支持的图片格式
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
        image_files.extend(image_folder.glob(ext))
    
    if not image_files:
        print(f"错误: 文件夹中没有找到图片: {image_folder}")
        return
    
    print(f"找到 {len(image_files)} 张图片")
    print(f"置信度阈值: {conf_threshold}")
    print()
    
    # 检测每张图片
    results_list = []
    for i, image_file in enumerate(sorted(image_files), 1):
        print(f"[{i}/{len(image_files)}] 检测: {image_file.name}")
        
        # 进行检测
        results = model(str(image_file), conf=conf_threshold)
        results_list.append((image_file, results))
        
        # 显示检测结果
        if len(results[0].boxes) > 0:
            print(f"  ✅ 检测到 {len(results[0].boxes)} 个火灾区域")
            
            # 显示每个检测框的信息
            for j, box in enumerate(results[0].boxes):
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                print(f"    区域{j+1}: 位置({x1:.0f}, {y1:.0f}) - ({x2:.0f}, {y2:.0f}), 置信度: {conf:.3f}")
        else:
            print(f"  ❌ 未检测到火灾")
        
        print()
    
    print("="*60)
    print("检测完成！")
    print()
    print("检测结果:")
    print("-"*60)
    
    total_detections = 0
    total_images = len(results_list)
    
    for image_file, results in results_list:
        detections = len(results[0].boxes)
        total_detections += detections
        
        status = "✅ 检测到" if detections > 0 else "❌ 未检测到"
        print(f"{status}: {image_file.name} ({detections} 个火灾区域）")
    
    print("-"*60)
    print(f"总计: {total_detections} 个火灾区域 / {total_images} 张图片")
    print(f"检测率: {total_detections/total_images*100:.1f}%")
    print()
    
    # 保存检测结果
    save_results(image_folder, results_list, model_path)
    
    return results_list

def save_results(image_folder, results_list, model_path):
    """
    保存检测结果
    
    参数:
        image_folder: 图片文件夹
        results_list: 检测结果列表
        model_path: 模型路径
    """
    print("保存检测结果...")
    
    # 创建结果文件夹
    results_folder = image_folder / 'results'
    results_folder.mkdir(exist_ok=True)
    
    # 保存每张图片的检测结果
    for image_file, results in results_list:
        # 保存标注后的图片
        annotated_image = results[0].plot()
        
        # 保存图片
        output_path = results_folder / f"detected_{image_file.name}"
        results[0].save(output_path)
        
        print(f"  已保存: {output_path}")
    
    print()

def main():
    """
    主函数
    """
    # 检测try文件夹中的图片
    image_folder = 'try'
    
    if not os.path.exists(image_folder):
        print(f"错误: 文件夹不存在: {image_folder}")
        return
    
    # 进行检测
    detect_fire_in_images(image_folder)

if __name__ == '__main__':
    main()