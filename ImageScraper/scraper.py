import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from PIL import Image
import io
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 1. 配置
LINKS_DIR = "links"  # 存放链接文件的文件夹
OUTPUT_DIR = "images"  # 图片保存总目录
TARGET_SIZE = (750, 750)  # 目标尺寸

# 2. 创建图片保存目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. 请求头（完全模拟浏览器）
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.redbubble.com/",
    "Cookie": "_dd_s=; ax_visitor=%7B%22firstVisitTs%22%3A1749519556571%2C%22lastVisitTs%22%3Anull%2C%22currentVisitStartTs%22%3A1749519556571%2C%22ts%22%3A1749519556571%2C%22visitCount%22%3A1%7D; _axwrt=ee44f2d3-8333-4cce-b86b-9959b6dfd0d0; _axidd=true"
}

def crop_image(image_data, bg_color):
    """
    将图片裁剪为实际内容区域，去掉f8f8f8背景色部分
    """
    try:
        # 从二进制数据创建图片对象
        img = Image.open(io.BytesIO(image_data))
        
        # 转换为RGB模式（如果不是的话）
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 获取图片尺寸
        width, height = img.size
        
        # 定义背景色（f8f8f8）
        # bg_color = (0, 0, 0)  # f8f8f8的RGB值
        
        # 找到实际内容的边界
        def find_content_bounds():
            # 从四个方向扫描，找到第一个非背景色的像素
            left = 2
            right = width - 4
            top = 2
            bottom = height - 4
            
            # 从左向右扫描
            for x in range(width):
                for y in range(height):
                    pixel = img.getpixel((x, y))
                    if pixel != bg_color:
                        left = x
                        break
                if left > 0:
                    break
            
            # 从右向左扫描
            for x in range(width-1, -1, -1):
                for y in range(height):
                    pixel = img.getpixel((x, y))
                    if pixel != bg_color:
                        right = x
                        break
                if right < width-1:
                    break
            
            # 从上向下扫描
            for y in range(height):
                for x in range(width):
                    pixel = img.getpixel((x, y))
                    if pixel != bg_color:
                        top = y
                        break
                if top > 0:
                    break
            
            # 从下向上扫描
            for y in range(height-1, -1, -1):
                for x in range(width):
                    pixel = img.getpixel((x, y))
                    if pixel != bg_color:
                        bottom = y
                        break
                if bottom < height-1:
                    break
            
            return (left, top, right + 1, bottom + 1)
        
        # 获取内容边界
        bounds = find_content_bounds()
        
        # 裁剪图片
        img = img.crop(bounds)
        
        # 将图片转换回二进制数据
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=95)
        return output.getvalue()
        
    except Exception as e:
        print(f"图片裁剪失败: {e}")
        return image_data  # 如果裁剪失败，返回原始图片数据

def extract_product_name(url):
    """
    从商品详情页链接中提取商品名部分
    例如：https://www.redbubble.com/i/tote-bag/SWIMMERS-by-Urbaun/39070653.A9G4R
    返回：SWIMMERS-by-Urbaun
    """
    try:
        parts = url.strip("/").split("/")
        return parts[-2]
    except Exception:
        return "unknown"

def find_target_image_url(soup):
    """
    优先查找class为ProductCard_productCardImage____xct ProductCard_imageHover__tpRo7的img标签，
    src中包含"st,"的链接；找不到再查找指定类名的picture标签中的jpg图片。
    """
    # 1. 优先查找img标签
    img_tags = soup.find_all("img", class_="ProductCard_productCardImage____xct ProductCard_imageHover__tpRo7")
    print(len(img_tags))
    # print(list(map(lambda x: x.get("src", ""), img_tags)))
    for img in img_tags:
        src = img.get("src", "")
        if "st," in src and src.endswith(".jpg"):
            return src

    # 2. 找不到再查找picture标签
    picture_tags = soup.find_all("picture", class_="Picture_picture__Gztgz Picture_rounded__PvnLg")
    if picture_tags:
        target_picture = picture_tags[-1]
        img = target_picture.find("img")
        if img and img.get("src", "").endswith(".jpg"):
            return img["src"]
    return None

def download_sticker_image(product_url, session, output_folder):
    """
    访问商品详情页，解析并下载目标图片（在特定div结构中的图片），图片命名为商品名，保存到指定文件夹
    """
    try:
        # 用Selenium获取渲染后的HTML
        html = get_rendered_html(product_url)
        soup = BeautifulSoup(html, "html.parser")

        # 优化后的查找图片链接逻辑
        target_img_url = find_target_image_url(soup)
        print(target_img_url)
        if not target_img_url:
            print(f"未找到目标图片: {product_url}")
            return False

        # 背景色替换
        # replace_img_url = target_img_url.replace('f8f8f8','000000')
        # 下载图片
        img_resp = session.get(target_img_url, headers=headers, timeout=15)
        img_resp.raise_for_status()
        
        # 裁剪图片
        cropped_image_data = img_resp.content
        # cropped_image_data = crop_image(cropped_image_data, (255, 255, 255))
        # cropped_image_data = crop_image(cropped_image_data, (248, 248, 248))
        # cropped_image_data = crop_image(cropped_image_data, (255, 255, 255))
        # cropped_image_data = crop_image(cropped_image_data, (0, 0, 0))

        # 提取商品名
        product_name = extract_product_name(product_url)
        # 过滤文件名中的非法字符，并去掉"-"符号
        safe_name = ''.join(c for c in product_name if c not in '\\/:*?\"<>|').replace('-', ' ')
        # 使用jpg作为文件后缀
        img_filename = f"{safe_name}.jpg"
        img_path = os.path.join(output_folder, img_filename)
        
        # 保存裁剪后的图片
        with open(img_path, "wb") as f:
            f.write(cropped_image_data)
        return True

    except Exception as e:
        print(f"下载失败: {product_url}，原因: {e}")
        return False

def process_links_file(links_file):
    """
    处理单个链接文件，下载所有图片到对应子文件夹
    """
    # 1. 生成输出子文件夹名（去掉.txt后缀）
    base_name = os.path.splitext(os.path.basename(links_file))[0]
    output_folder = os.path.join(OUTPUT_DIR, base_name)
    os.makedirs(output_folder, exist_ok=True)

    # 2. 读取所有链接
    with open(links_file, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]

    print(f"\n处理文件: {links_file}，共 {len(links)} 个链接，图片将保存到: {output_folder}")
    session = requests.Session()
    success_count = 0
    for url in tqdm(links, desc=f"{base_name} 下载进度"):
        if download_sticker_image(url, session, output_folder):
            success_count += 1
    print(f"文件 {links_file} 下载完成，成功下载 {success_count} 张图片。\n")

def main():
    """
    主程序入口，遍历所有链接文件
    """
    if not os.path.exists(LINKS_DIR):
        print(f"未找到 {LINKS_DIR} 文件夹！")
        return
    files = [os.path.join(LINKS_DIR, f) for f in os.listdir(LINKS_DIR) if f.endswith(".txt")]
    if not files:
        print(f"{LINKS_DIR} 文件夹下没有 .txt 链接文件！")
        return
    for links_file in files:
        process_links_file(links_file)

def get_rendered_html(url):
    options = Options()
    # options.add_argument('--headless')  # 无界面模式
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    try:
        # 等待目标img标签出现（最长等10秒）
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "ProductCard_productCardImage____xct")
            )
        )
        # 模拟页面滚动，触发懒加载（如有需要）
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 等待图片加载
    except Exception as e:
        print("等待图片标签超时:", e)
    html = driver.page_source
    driver.quit()
    return html

if __name__ == "__main__":
    main()