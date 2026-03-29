from ultralytics import YOLO
import os
import yaml

def train_yolo():
    """
    训练YOLO模型
    """
    print("开始训练YOLO模型...")
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
    
    # 开始训练
    print("开始训练...")
    print("注意: 跳过字体下载，使用系统默认字体")
    
    results = model.train(
        data=yaml_path,
        epochs=100,
        imgsz=640,
        batch=16,
        device='cpu',  # 如果有GPU，可以改为 '0' 或 'cuda'
        project='runs',
        name='detect',
        exist_ok=True,
        plots=False,  # 禁用绘图以避免字体问题
        verbose=True
    )
    
    print("\n训练完成！")
    print(f"模型保存在: {results.save_dir}")

if __name__ == '__main__':
    train_yolo()