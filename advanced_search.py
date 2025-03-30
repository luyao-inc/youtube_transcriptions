#!/usr/bin/env python3
"""
高级YouTube视频搜索工具

使用Selenium实现更可靠的YouTube视频搜索，
适用于普通网络请求不可用的情况。
支持从keywords.txt文件读取多个关键词，第一行包含关键词（逗号分隔），
第二行包含每次抓取的视频数量，并要求视频同时包含所有关键词。
"""

import os
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def read_keywords_config(file_path):
    """
    从文件中读取关键词和配置信息
    
    Args:
        file_path: 关键词文件的路径
        
    Returns:
        包含关键词列表和视频数量的元组 (keywords, limit)
    """
    keywords = ["紫微斗数"]
    limit = 20
    
    if not os.path.exists(file_path):
        print(f"关键词文件 {file_path} 不存在，将使用默认关键词：'紫微斗数' 和默认数量：20")
        return keywords, limit
    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        
        # 读取第一行关键词
        if lines and lines[0].strip():
            keywords_line = lines[0].strip()
            keywords = [k.strip() for k in keywords_line.split(',') if k.strip()]
        
        # 读取第二行视频数量
        if len(lines) > 1 and lines[1].strip():
            try:
                limit = int(lines[1].strip())
                if limit <= 0:
                    print(f"视频数量配置无效：{lines[1].strip()}，将使用默认值：20")
                    limit = 20
            except ValueError:
                print(f"视频数量配置无效：{lines[1].strip()}，将使用默认值：20")
                limit = 20
    
    if not keywords:
        print("关键词文件为空，将使用默认关键词：'紫微斗数'")
        keywords = ["紫微斗数"]
        
    return keywords, limit

def read_existing_links(file_path):
    """读取现有的YouTube链接"""
    existing_links = set()
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and line.startswith('http'):
                    existing_links.add(line)
    
    return existing_links

def save_links(file_path, links):
    """保存链接到文件"""
    mode = 'a' if os.path.exists(file_path) else 'w'
    
    with open(file_path, mode, encoding='utf-8') as file:
        for link in links:
            file.write(f"{link}\n")

def search_youtube_with_selenium(keywords, max_results=20):
    """
    使用Selenium搜索YouTube视频
    
    Args:
        keywords: 搜索关键词列表
        max_results: 最多返回的结果数量
        
    Returns:
        包含视频链接的列表
    """
    # 合并关键词为一个搜索字符串
    combined_keyword = ' '.join(keywords)
    print(f"正在使用Selenium搜索同时包含关键词 '{combined_keyword}' 的YouTube视频...")
    
    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        # 初始化浏览器
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # 构建搜索URL
        search_url = f"https://www.youtube.com/results?search_query={'+'.join(combined_keyword.split())}"
        driver.get(search_url)
        
        # 等待页面加载
        time.sleep(3)
        
        # 滚动页面以加载更多结果
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(1)
        
        # 查找视频链接和标题
        video_elements = driver.find_elements(By.XPATH, "//a[@id='video-title']")
        
        # 收集所有视频链接和标题
        candidate_videos = []
        for element in video_elements:
            href = element.get_attribute('href')
            title = element.get_attribute('title')
            if href and "watch?v=" in href:
                candidate_videos.append((href, title))
        
        # 筛选同时包含所有关键词的视频
        filtered_videos = []
        print(f"正在验证视频是否包含所有关键词...")
        
        for href, title in candidate_videos:
            if len(filtered_videos) >= max_results:
                break
            
            # 检查视频详情页面是否包含所有关键词
            driver.get(href)
            time.sleep(2)  # 等待页面加载
            
            page_text = driver.page_source.lower()
            all_keywords_found = True
            
            for keyword in keywords:
                if keyword.lower() not in page_text:
                    all_keywords_found = False
                    break
            
            if all_keywords_found:
                filtered_videos.append(href)
                print(f"找到符合条件的视频: {href}")
        
        driver.quit()
        return filtered_videos
    
    except Exception as e:
        print(f"Selenium搜索出错: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='使用Selenium搜索YouTube视频并保存链接')
    parser.add_argument('--keywords-file', default='keywords.txt', help='关键词文件路径 (默认: keywords.txt)')
    parser.add_argument('--limit', type=int, help='每次最多添加的新链接数量 (将覆盖配置文件中的设置)')
    parser.add_argument('--output', default='videos.txt', help='输出文件路径 (默认: videos.txt)')
    
    args = parser.parse_args()
    
    # 读取关键词和配置
    keywords, config_limit = read_keywords_config(args.keywords_file)
    print(f"将搜索以下关键词: {', '.join(keywords)}")
    
    # 优先使用命令行参数的limit，如果没有则使用配置文件中的limit
    limit = args.limit if args.limit is not None else config_limit
    print(f"每次最多添加 {limit} 个新链接")
    
    # 读取现有链接
    existing_links = read_existing_links(args.output)
    print(f"已存在 {len(existing_links)} 个链接")
    
    # 搜索新链接
    all_links = search_youtube_with_selenium(keywords, limit * 2)  # 多获取一些以防重复
    
    # 过滤掉已存在的链接
    new_links = [link for link in all_links if link not in existing_links]
    
    # 限制数量
    new_links = new_links[:limit]
    
    # 保存新链接
    if new_links:
        save_links(args.output, new_links)
        print(f"已添加 {len(new_links)} 个新链接到 {args.output}")
        for i, link in enumerate(new_links, 1):
            print(f"{i}. {link}")
    else:
        print("未找到新链接")
    
if __name__ == "__main__":
    main() 