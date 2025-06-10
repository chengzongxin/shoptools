from PIL import Image, ImageDraw
import os

def create_icon():
    # 创建一个 256x256 的图像
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 绘制一个简单的图标（这里画一个圆形）
    margin = 20
    draw.ellipse([margin, margin, size-margin, size-margin], 
                 fill=(52, 152, 219))  # 使用蓝色
    
    # 保存为不同格式
    if os.name == 'nt':  # Windows
        image.save('icon.ico', format='ICO', sizes=[(256, 256)])
    else:  # macOS
        image.save('icon.icns', format='ICNS')

if __name__ == '__main__':
    create_icon() 