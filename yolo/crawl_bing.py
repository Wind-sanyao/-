import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, quote
import ssl
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

def download_image(url, save_path):
    """
    下载单张图片
    """
    try:
        # 使用多个请求头尝试
        headers_list = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://cn.bing.com/',
                'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            },
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://cn.bing.com/',
                'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            }
        ]
        
        for headers in headers_list:
            try:
                response = requests.get(url, headers=headers, timeout=15, verify=False)
                response.raise_for_status()
                
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                return True
            except:
                continue
        
        return False
    except Exception as e:
        print(f"下载失败: {url}")
        print(f"错误: {e}")
        return False

def crawl_images_from_bing():
    """
    从Bing图片搜索爬取房屋图片
    """
    print("="*60)
    print("Bing图片搜索爬虫")
    print("="*60)
    print()
    
    # 搜索关键词
    search_query = "房屋"
    encoded_query = quote(search_query)
    
    # Bing图片搜索URL
    base_url = f'https://cn.bing.com/images/search?q={encoded_query}&qs=n&form=QBIRMH&sp=-1&lq=0&pq={encoded_query}&sc=10-2&first=1'
    
    print(f"搜索关键词: {search_query}")
    print(f"搜索URL: {base_url}")
    print()
    
    # 创建保存文件夹
    save_folder = 'datasets/bvn/images/train'
    os.makedirs(save_folder, exist_ok=True)
    print(f"保存文件夹: {save_folder}")
    print()
    
    # 请求网页
    print("正在获取网页...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        session = requests.Session()
        session.verify = False
        
        response = session.get(base_url, headers=headers, timeout=20)
        response.raise_for_status()
        print("网页获取成功！")
        print()
    except Exception as e:
        print(f"网页获取失败: {e}")
        print()
        print("="*60)
        print("建议:")
        print("  1. 检查网络连接")
        print("  2. 尝试手动下载图片")
        print("  3. 使用其他图片源")
        print()
        return
    
    # 解析网页
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有图片
    print("正在查找图片...")
    image_urls = []
    
    # 方法1: 查找所有img标签
    images = soup.find_all('img')
    for img in images:
        # 获取图片URL
        img_url = img.get('src') or img.get('data-src') or img.get('data-src')
        
        if img_url and 'tse' not in img_url.lower():  # 排除缩略图
            # 转换为绝对URL
            if not img_url.startswith('http'):
                img_url = urljoin(base_url, img_url)
            
            # 过滤Bing的图片
            if 'bing.com' not in img_url.lower() and 'msn.com' not in img_url.lower():
                image_urls.append(img_url)
    
    # 去重
    image_urls = list(dict.fromkeys(image_urls))
    
    print(f"找到 {len(image_urls)} 张图片")
    print()
    
    if not image_urls:
        print("错误: 没有找到图片")
        print("请检查网页结构是否改变")
        return
    
    # 限制数量
    image_urls = image_urls[:60]
    print(f"将下载前 {len(image_urls)} 张图片")
    print()
    
    # 下载图片
    success_count = 0
    start_num = 1100
    
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
            time.sleep(1)  # 避免请求过快
    
    print()
    print("="*60)
    print(f"下载完成！")
    print(f"  成功: {success_count}/{len(image_urls)}")
    print(f"  保存位置: {save_folder}")
    print(f"  编号范围: {start_num} - {start_num + len(image_urls) - 1}")
    print()

if __name__ == '__main__':
    crawl_images_from_bing()