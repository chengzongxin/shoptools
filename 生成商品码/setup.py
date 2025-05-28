from setuptools import setup

setup(
    name="product_crawler",
    version="1.0.0",
    packages=["product_crawler"],
    install_requires=[
        "requests",
        "pandas",
        "openpyxl",
        "tkinter",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="商品数据爬取工具",
    keywords="crawler, gui, excel",
    python_requires=">=3.6",
) 