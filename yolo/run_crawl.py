from crawl_images import crawl_images_from_url

# 使用你提供的URL和XPath
base_url = 'https://cn.bing.com/images/search?q=%E6%88%BF%E5%B1%8B&qs=n&form=QBIRMH&sp=-1&lq=0&pq=%E6%88%BF%E5%B1%8B&sc=10-2&cvid=B43D2B9937234FF192EA470204066C9D&first=1&cw=1430&ch=519'

# 使用XPath选择器
image_selector = '//*[@id="mmComponent_images_1"]/ul[5]/li[1]/div/div[1]/a/div/img'

# 爬取60张图片，从1100开始编号
crawl_images_from_url(
    base_url=base_url,
    image_selector=image_selector,
    start_num=1100,
    count=60,
    save_folder='datasets/bvn/images/train'
)