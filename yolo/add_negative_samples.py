import os
import shutil
import glob

def add_negative_samples():
    """
    添加负样本到训练集
    支持批量添加：1-300火灾，301-400正常照片
    """
    print("="*60)
    print("添加负样本到训练集")
    print("="*60)
    print()
    
    # 负样本文件夹
    negative_folder = 'negative_samples'
    
    # 训练集图片和标签文件夹
    train_images = 'datasets/bvn/images/train'
    train_labels = 'datasets/bvn/labels/train'
    
    # 创建负样本文件夹
    if not os.path.exists(negative_folder):
        os.makedirs(negative_folder)
        print(f"已创建负样本文件夹: {negative_folder}")
        print()
        print("="*60)
        print("负样本说明")
        print("="*60)
        print()
        print("什么是负样本？")
        print("  负样本 = 没有火灾的图片")
        print()
        print("负样本应该包括：")
        print("  ✓ 正常的房屋、建筑、室内场景")
        print("  ✓ 白天、夜晚的不同光照条件")
        print("  ✓ 室内、室外的不同场景")
        print("  ✓ 容易误判的物体：红色、橙色、黄色的物体")
        print("  ✓ 烟雾但不是火灾的场景（雾天、蒸汽等）")
        print()
        print("="*60)
        print("数量建议")
        print("="*60)
        print()
        print("  火灾照片: 300张")
        print("  负样本: 75-100张（推荐）")
        print("  比例: 1:3 到 1:4（负样本:正样本）")
        print()
        print("  不需要1:1的比例，那样负样本太多了")
        print()
        print("="*60)
        print("如何使用")
        print("="*60)
        print()
        print("  1. 将没有火灾的图片放到此文件夹中")
        print("  2. 支持的格式: .jpg, .jpeg, .png, .webp")
        print("  3. 运行此脚本添加到训练集")
        print("  4. 重新训练模型")
        print()
        return
    
    # 检查负样本文件夹中的图片
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
        image_files.extend(glob.glob(os.path.join(negative_folder, ext)))
    
    if not image_files:
        print(f"负样本文件夹为空: {negative_folder}")
        print("请将没有火灾的图片放到此文件夹中")
        return
    
    print(f"找到 {len(image_files)} 张负样本图片")
    print()
    
    # 统计当前训练集数量
    existing_images = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
        existing_images.extend(glob.glob(os.path.join(train_images, ext)))
    
    print(f"当前训练集已有 {len(existing_images)} 张图片")
    print()
    
    # 复制图片到训练集
    copied_count = 0
    for img_file in sorted(image_files):
        img_name = os.path.basename(img_file)
        dst_img = os.path.join(train_images, img_name)
        
        # 检查是否已存在
        if os.path.exists(dst_img):
            print(f"跳过（已存在）: {img_name}")
            continue
        
        # 复制图片
        shutil.copy2(img_file, dst_img)
        
        # 创建空的标签文件（负样本没有目标）
        label_name = os.path.splitext(img_name)[0] + '.txt'
        label_path = os.path.join(train_labels, label_name)
        
        # 创建空标签文件
        with open(label_path, 'w') as f:
            pass  # 空文件表示没有目标
        
        copied_count += 1
        print(f"已添加: {img_name}")
    
    print()
    print("="*60)
    print(f"成功添加 {copied_count} 张负样本！")
    print()
    print(f"新的训练集总数: {len(existing_images) + copied_count} 张")
    print(f"  - 火灾照片: {len(existing_images)} 张")
    print(f"  - 负样本: {copied_count} 张")
    print(f"  - 比例: 1:{len(existing_images)/copied_count:.1f}" if copied_count > 0 else "")
    print()
    print("="*60)
    print("下一步")
    print("="*60)
    print()
    print("负样本已添加完成！")
    print()
    print("建议:")
    print("  1. 检查负样本数量是否合适（推荐75-100张）")
    print("  2. 确保负样本包含各种场景和容易误判的物体")
    print("  3. 重新训练模型:")
    print("     python train_yolo.py")
    print("     或")
    print("     python train_yolo_v2.py (优化参数)")
    print()

if __name__ == '__main__':
    add_negative_samples()