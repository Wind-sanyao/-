from ultralytics import YOLO
import os
import yaml
import torch

def train_yolo_with_better_params():
    """
    使用优化参数训练YOLO模型（减少假阳性）
    """
    print("开始训练YOLO模型（优化参数）...")
    print("="*60)
    
    # 获取当前工作目录
    cwd = os.getcwd()
    print(f"当前工作目录: {cwd}")
    
    # 生成YAML配置文件
    yaml_path = os.path.join(cwd, 'yolo-bvn.yaml')
    
    data_config = {
        'path': os.path.join(cwd, 'datasets', 'bvn', 'images'),
        'train': 'train',
        'val': 'val',
        'names': {0: 'fire'}
    }
    
    print(f"数据集路径: {data_config['path']}")
    
    # 检查目录是否存在
    train_dir = os.path.join(data_config['path'], 'train')
    val_dir = os.path.join(data_config['path'], 'val')
    
    print(f"训练集目录: {train_dir}")
    print(f"验证集目录: {val_dir}")
    
    if not os.path.exists(train_dir):
        print(f"错误: 训练集目录不存在: {train_dir}")
        return
    
    if not os.path.exists(val_dir):
        print(f"错误: 验证集目录不存在: {val_dir}")
        return
    
    # 写入YAML文件
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data_config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"YAML配置文件已生成: {yaml_path}")
    
    # 加载预训练模型
    print("加载预训练模型 yolov8n.pt...")
    model = YOLO('yolov8n.pt')
    
    # 开始训练（优化参数）
    print("开始训练...")
    print("注意: 跳过字体下载，使用系统默认字体")
    
    results = model.train(
        data=yaml_path,
        epochs=100,
        imgsz=640,
        batch=16,
        device='cuda' if torch.cuda.is_available() else 'cpu',  # 自动检测并使用GPU
        project='runs',
        name='detect_v2',
        exist_ok=True,
        plots=False,
        verbose=True,
        
        # 优化参数（减少假阳性）
        conf=0.25,  # 置信度阈值（默认0.25，可以提高到0.3-0.5）
        iou=0.7,  # IoU阈值（默认0.7，可以提高）
        patience=50,  # 早停耐心值（默认100，降低可以更快收敛）
        single_cls=False,  # 单类别检测
        rect=False,  # 矩形训练
        cos_lr=True,  # 余弦学习率调度
        close_mosaic=10,  # 最后10轮关闭mosaic增强
        mixup=0.0,  # Mixup增强（减少过拟合）
        copy_paste=0.0,  # Copy-paste增强（减少过拟合）
        dropout=0.0,  # Dropout率
        weight_decay=0.0005,  # 权重衰减
        warmup_epochs=3.0,  # 预热轮数
        lr0=0.01,  # 初始学习率
        lrf=0.01,  # 最终学习率
        momentum=0.937,  # 动量
        hsv_h=0.015,  # HSV色调增强
        hsv_s=0.7,  # HSV饱和度增强
        hsv_v=0.4,  # HSV明度增强
        degrees=0.0,  # 旋转角度
        translate=0.1,  # 平移
        scale=0.5,  # 缩放
        shear=0.0,  # 剪切
        perspective=0.0,  # 透视变换
        flipud=0.0,  # 垂直翻转
        fliplr=0.5,  # 水平翻转
        bgr=0.0,  # BGR转换
        mosaic=1.0  # Mosaic增强
    )
    
    print("\n训练完成！")
    print(f"模型保存在: {results.save_dir}")

if __name__ == '__main__':
    train_yolo_with_better_params()