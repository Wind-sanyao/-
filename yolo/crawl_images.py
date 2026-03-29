import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin
from pathlib import Path

def download_image(url, save_path):
    """
    下载单张图片
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"下载失败: {url}")
        print(f"错误: {e}")
        return False

def crawl_images_from_url(base_url, image_selector, start_num=1100, count=60, save_folder='datasets/bvn/images/train'):
    """
    从网页爬取图片
    
    参数:
        base_url: 目标网页URL
        image_selector: 图片选择器（CSS选择器或XPath）
        start_num: 起始编号（默认1100）
        count: 图片数量（默认60）
        save_folder: 保存文件夹（默认datasets/bvn/images/train）
    """
    print("="*60)
    print("网页图片爬虫")
    print("="*60)
    print()
    
    # 创建保存文件夹
    os.makedirs(save_folder, exist_ok=True)
    
    print(f"目标URL: {base_url}")
    print(f"图片选择器: {image_selector}")
    print(f"起始编号: {start_num}")
    print(f"图片数量: {count}")
    print(f"保存文件夹: {save_folder}")
    print()
    
    # 请求网页
    print("正在获取网页...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        print("网页获取成功！")
        print()
    except Exception as e:
        print(f"网页获取失败: {e}")
        return
    
    # 解析网页
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找图片
    print("正在查找图片...")
    if image_selector.startswith('//'):
        # XPath选择器
        from lxml import etree
        tree = etree.HTML(str(soup))
        images = tree.xpath(image_selector)
        image_urls = [img.get('src') or img.get('data-src') for img in images]
    else:
        # CSS选择器
        images = soup.select(image_selector)
        image_urls = [img.get('src') or img.get('data-src') for img in images]
    
    # 过滤空URL
    image_urls = [url for url in image_urls if url]
    
    print(f"找到 {len(image_urls)} 张图片")
    print()
    
    if not image_urls:
        print("错误: 没有找到图片")
        print("请检查图片选择器是否正确")
        return
    
    # 限制数量
    image_urls = image_urls[:count]
    print(f"将下载前 {len(image_urls)} 张图片")
    print()
    
    # 下载图片
    success_count = 0
    for i, img_url in enumerate(image_urls):
        # 转换为绝对URL
        if not img_url.startswith('http'):
            img_url = urljoin(base_url, img_url)
        
        # 生成文件名
        file_num = start_num + i
        ext = os.path.splitext(img_url)[1]
        if not ext:
            ext = '.jpg'  # 默认扩展名
        
        filename = f"{file_num}{ext}"
        save_path = os.path.join(save_folder, filename)
        
        # 检查是否已存在
        if os.path.exists(save_path):
            print(f"跳过（已存在）: {filename}")
            success_count += 1
            continue
        
        # 下载图片
        print(f"下载 [{i+1}/{len(image_urls)}]: {filename}")
        if download_image(img_url, save_path):
            success_count += 1
            time.sleep(0.5)  # 避免请求过快
    
    print()
    print("="*60)
    print(f"下载完成！")
    print(f"  成功: {success_count}/{len(image_urls)}")
    print(f"  保存位置: {save_folder}")
    print(f"  编号范围: {start_num} - {start_num + len(image_urls) - 1}")
    print()

def crawl_images_from_url_list(url_file, start_num=1100, save_folder='datasets/bvn/images/train'):
    """
    从URL列表文件下载图片
    
    参数:
        url_file: 包含图片URL的文本文件
        start_num: 起始编号（默认1100）
        save_folder: 保存文件夹（默认datasets/bvn/images/train）
    """
    print("="*60)
    print("URL列表图片下载")
    print("="*60)
    print()
    
    # 创建保存文件夹
    os.makedirs(save_folder, exist_ok=True)
    
    # 读取URL列表
    if not os.path.exists(url_file):
        print(f"错误: 文件不存在: {url_file}")
        return
    
    with open(url_file, 'r', encoding='utf-8') as f:
        image_urls = [line.strip() for line in f if line.strip()]
    
    print(f"URL文件: {url_file}")
    print(f"找到 {len(image_urls)} 个URL")
    print(f"起始编号: {start_num}")
    print(f"保存文件夹: {save_folder}")
    print()
    
    # 下载图片
    success_count = 0
    for i, img_url in enumerate(image_urls):
        # 生成文件名
        file_num = start_num + i
        ext = os.path.splitext(img_url)[1]
        if not ext:
            ext = '.jpg'  # 默认扩展名
        
        filename = f"{file_num}{ext}"
        save_path = os.path.join(save_folder, filename)
        
        # 检查是否已存在
        if os.path.exists(save_path):
            print(f"跳过（已存在）: {filename}")
            success_count += 1
            continue
        
        # 下载图片
        print(f"下载 [{i+1}/{len(image_urls)}]: {filename}")
        if download_image(img_url, save_path):
            success_count += 1
            time.sleep(0.5)  # 避免请求过快
    
    print()
    print("="*60)
    print(f"下载完成！")
    print(f"  成功: {success_count}/{len(image_urls)}")
    print(f"  保存位置: {save_folder}")
    print(f"  编号范围: {start_num} - {start_num + len(image_urls) - 1}")
    print()

if __name__ == '__main__':
    print("请选择爬取方式:")
    print("1. 从单个网页爬取（需要提供URL和图片选择器）")
    print("2. 从URL列表文件下载（需要提供包含URL的文本文件）")
    print()
    
    choice = input("请输入选项 (1/2): ").strip()
    
    if choice == '1':
        print()
        print("请提供以下信息:")
        print()
        
        base_url = input("目标网页URL: ").strip()
        image_selector = input("图片选择器（CSS选择器，如 img.fire-image）: ").strip()
        
        start_num = input("起始编号（默认1100）: ").strip()
        start_num = int(start_num) if start_num else 1100
        
        count = input("图片数量（默认60）: ").strip()
        count = int(count) if count else 60
        
        print()
        crawl_images_from_url(base_url, image_selector, start_num, count)
    
    elif choice == '2':
        print()
        print("请提供以下信息:")
        print()
        
        url_file = input("URL列表文件路径（如 image_urls.txt）: ").strip()
        
        start_num = input("起始编号（默认1100）: ").strip()
        start_num = int(start_num) if start_num else 1100
        
        print()
        crawl_images_from_url_list(url_file, start_num)
    
    else:
        print("无效选项")