from ultralytics import YOLO
import os

print("="*60)
print("火灾检测模型批量测试（高置信度模式）")
print("="*60)

model_path = 'runs/detect/weights/best.pt'
image_folder = 'try'
confidence_threshold = 0.50  # 只显示置信度 > 50% 的结果

print(f"加载模型: {model_path}")
model = YOLO(model_path)
print("模型加载成功！")
print()
print(f"置信度阈值: {confidence_threshold:.0%}")
print()

if not os.path.exists(image_folder):
    print(f"错误: 文件夹不存在: {image_folder}")
else:
    print(f"测试文件夹: {image_folder}")
    print()
    
    # 获取所有710-719的图片
    image_files = []
    for i in range(710, 720):
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
            pattern = os.path.join(image_folder, f"{i}.{ext.replace('*.', '')}")
            if os.path.exists(pattern):
                image_files.append(pattern)
                break
    
    if not image_files:
        print("错误: 没有找到710-719的图片文件")
    else:
        print(f"找到 {len(image_files)} 张图片")
        print()
        print("="*60)
        print()
        
        # 逐个测试
        for image_path in sorted(image_files):
            print(f"测试图片: {os.path.basename(image_path)}")
            
            # 使用高置信度阈值进行预测
            results = model(image_path, conf=confidence_threshold)
            
            for r in results:
                num_detections = len(r.boxes)
                print(f"  检测到 {num_detections} 个目标 (置信度 > {confidence_threshold:.0%})")
                
                if num_detections > 0:
                    for i, box in enumerate(r.boxes):
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        class_name = model.names[cls_id]
                        
                        print(f"    目标 {i+1}: {class_name} (置信度: {conf:.2%})")
                else:
                    print(f"  ✅ 未检测到火灾")
            
            print()
        
        print("="*60)
        print()
        print("所有测试完成！")
        print(f"结果已保存到: runs/detect/predict/")
        print()
        
        # 显示最后一张图片的结果
        print("显示最后一张图片的检测结果...")
        results[-1].show()