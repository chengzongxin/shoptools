import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# 1. 配置
LINKS_DIR = "links"  # 存放链接文件的文件夹
OUTPUT_DIR = "images"  # 图片保存总目录

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

def download_sticker_image(product_url, session, output_folder):
    """
    访问商品详情页，解析并下载目标图片（在特定div结构中的图片），图片命名为商品名，保存到指定文件夹
    """
    try:
        resp = session.get(product_url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 查找所有具有指定类名的picture标签
        picture_tags = soup.find_all("picture", class_="Picture_picture__Gztgz Picture_rounded__PvnLg")
        
        if not picture_tags:
            print(f"未找到目标picture标签: {product_url}")
            return False
            
        # 获取最后一个picture标签
        target_picture = picture_tags[-1]
        
        # 优先查找webp格式
        source = target_picture.find("source")
        target_img_url = None
        if source and source.get("srcset"):
            target_img_url = source["srcset"]
        else:
            # 如果没有webp，查找jpg格式
            img = target_picture.find("img")
            if img and img.get("src"):
                target_img_url = img["src"]

        if not target_img_url:
            print(f"未找到图片URL: {product_url}")
            return False

        # 下载图片
        img_resp = session.get(target_img_url, headers=headers, timeout=15)
        img_resp.raise_for_status()

        # 提取商品名
        product_name = extract_product_name(product_url)
        # 过滤文件名中的非法字符
        safe_name = ''.join(c for c in product_name if c not in '\\/:*?\"<>|')
        # 获取图片后缀
        img_ext = target_img_url.split(".")[-1].split("?")[0]
        img_filename = f"{safe_name}.{img_ext}"
        img_path = os.path.join(output_folder, img_filename)
        with open(img_path, "wb") as f:
            f.write(img_resp.content)
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

if __name__ == "__main__":
    main()