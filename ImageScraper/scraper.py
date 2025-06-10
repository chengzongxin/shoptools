import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# 1. 配置
LINKS_DIR = "links"  # 存放链接文件的文件夹
OUTPUT_DIR = "images"  # 图片保存目录

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

def get_all_links():
    """
    遍历 links 文件夹下所有 txt 文件，读取所有商品详情页链接
    """
    all_links = []
    for filename in os.listdir(LINKS_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(LINKS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    url = line.strip()
                    if url:
                        all_links.append(url)
    return all_links

def download_sticker_image(product_url, session, idx):
    """
    访问商品详情页，解析并下载目标图片（src 包含 flat,），图片命名为商品名
    """
    try:
        resp = session.get(product_url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 查找所有目标 class 的图片
        img_tags = soup.find_all("img", class_="Picture_fullWidth__T0hym")
        target_img = None
        for img in img_tags:
            src = img.get("src", "")
            print(src)
            if "flat," in src:
                target_img = img
                break

        if not target_img or not target_img.get("src"):
            print(f"未找到目标图片: {product_url}")
            return False

        img_url = target_img["src"]

        # 下载图片
        img_resp = session.get(img_url, headers=headers, timeout=15)
        img_resp.raise_for_status()

        # 提取商品名
        product_name = extract_product_name(product_url)
        # 获取图片后缀
        img_ext = img_url.split(".")[-1].split("?")[0]
        img_filename = f"{product_name}.{img_ext}"
        img_path = os.path.join(OUTPUT_DIR, img_filename)
        with open(img_path, "wb") as f:
            f.write(img_resp.content)
        return True

    except Exception as e:
        print(f"下载失败: {product_url}，原因: {e}")
        return False

def extract_product_name(url):
    """
    从商品详情页链接中提取商品名部分
    例如：https://www.redbubble.com/i/tote-bag/SWIMMERS-by-Urbaun/39070653.A9G4R
    返回：SWIMMERS-by-Urbaun
    """
    try:
        parts = url.strip("/").split("/")
        # 倒数第二段就是商品名
        return parts[-2]
    except Exception:
        return "unknown"

def main():
    """
    主程序入口
    """
    all_links = get_all_links()
    print(f"共发现 {len(all_links)} 个商品链接，开始下载...")

    session = requests.Session()
    success_count = 0

    for idx, url in enumerate(tqdm(all_links, desc="下载进度")):
        if download_sticker_image(url, session, idx):
            success_count += 1

    print(f"下载完成，成功下载 {success_count} 张图片。")

if __name__ == "__main__":
    main()