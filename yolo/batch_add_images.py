import os
import shutil

def batch_add_images(source_folder, target_folder, start_num=1100, count=60):
    """
    批量添加图片到训练集
    
    参数:
        source_folder: 源文件夹
        target_folder: 目标文件夹（datasets/bvn/images/train）
        start_num: 起始编号（默认1100）
        count: 添加数量（默认60）
    """
    print("="*60)
    print("批量添加图片到训练集")
    print("="*60)
    print()
    
    # 创建目标文件夹
    os.makedirs(target_folder, exist_ok=True)
    
    # 获取源文件夹中的所有图片
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.bmp']:
        import glob
        image_files.extend(glob.glob(os.path.join(source_folder, ext)))
    
    if not image_files:
        print(f"错误: 源文件夹为空: {source_folder}")
        return
    
    print(f"源文件夹: {source_folder}")
    print(f"目标文件夹: {target_folder}")
    print(f"找到 {len(image_files)} 张图片")
    print(f"起始编号: {start_num}")
    print(f"添加数量: {count}")
    print()
    
    # 限制数量
    image_files = image_files[:count]
    
    # 复制图片
    added_count = 0
    for i, src_file in enumerate(sorted(image_files)):
        # 生成新文件名
        ext = os.path.splitext(src_file)[1]
        new_filename = f"{start_num + i}{ext}"
        dst_file = os.path.join(target_folder, new_filename)
        
        # 检查是否已存在
        if os.path.exists(dst_file):
            print(f"跳过（已存在）: {new_filename}")
            added_count += 1
            continue
        
        # 复制文件
        shutil.copy2(src_file, dst_file)
        print(f"已添加: {os.path.basename(src_file)} -> {new_filename}")
        added_count += 1
    
    print()
    print("="*60)
    print(f"添加完成！")
    print(f"  成功: {added_count}/{len(image_files)}")
    print(f"  编号范围: {start_num} - {start_num + len(image_files) - 1}")
    print(f"  保存位置: {target_folder}")
    print()

if __name__ == '__main__':
    print("请选择操作:")
    print("1. 从 'try' 文件夹添加图片（10张）")
    print("2. 从 'downloaded_images' 文件夹添加图片")
    print("3. 自定义源文件夹")
    print()
    
    choice = input("请输入选项 (1/2/3): ").strip()
    
    if choice == '1':
        source_folder = 'try'
        target_folder = 'datasets/bvn/images/train'
        batch_add_images(source_folder, target_folder, start_num=1100, count=10)
    
    elif choice == '2':
        source_folder = 'downloaded_images'
        target_folder = 'datasets/bvn/images/train'
        batch_add_images(source_folder, target_folder, start_num=1100, count=60)
    
    elif choice == '3':
        source_folder = input("源文件夹路径: ").strip()
        target_folder = input("目标文件夹路径（默认 datasets/bvn/images/train）: ").strip()
        if not target_folder:
            target_folder = 'datasets/bvn/images/train'
        
        start_num = input("起始编号（默认1100）: ").strip()
        start_num = int(start_num) if start_num else 1100
        
        count = input("添加数量（默认60）: ").strip()
        count = int(count) if count else 60
        
        batch_add_images(source_folder, target_folder, start_num, count)
    
    else:
        print("无效选项")