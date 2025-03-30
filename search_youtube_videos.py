#!/usr/bin/env python3
"""
视频搜索工具

此脚本用于在YouTube和抖音搜索包含特定关键词的视频，
关键词从keywords.txt文件中读取，多个关键词之间用逗号分隔，
文件第二行可以指定每次最多抓取的视频数量，
结果保存到videos.txt文件中。
"""

import os
import re
import argparse
import requests
from bs4 import BeautifulSoup

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
    """
    读取现有的视频链接
    
    Args:
        file_path: videos.txt文件的路径
        
    Returns:
        包含所有现有链接的集合
    """
    existing_links = set()
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and line.startswith('http'):
                    existing_links.add(line)
    
    return existing_links

def save_links(file_path, links):
    """
    保存链接到文件
    
    Args:
        file_path: videos.txt文件的路径
        links: 要保存的链接列表
    """
    mode = 'a' if os.path.exists(file_path) else 'w'
    
    with open(file_path, mode, encoding='utf-8') as file:
        for link in links:
            file.write(f"{link}\n")

def search_videos(keywords, platform='youtube', max_results=20):
    """
    搜索视频，支持YouTube和抖音
    
    Args:
        keywords: 搜索关键词列表
        platform: 搜索平台，可选 'youtube' 或 'douyin'
        max_results: 最多返回的结果数量
        
    Returns:
        包含视频链接的列表
    """
    combined_keyword = ' '.join(keywords)
    
    if platform == 'youtube':
        return search_youtube(keywords, max_results)
    elif platform == 'douyin':
        print(f"抖音搜索功能尚未实现，将使用YouTube搜索代替")
        return search_youtube(keywords, max_results)
    else:
        print(f"不支持的平台: {platform}，将使用YouTube搜索代替")
        return search_youtube(keywords, max_results)

def search_youtube(keywords, max_results=20):
    """
    使用网页抓取搜索YouTube视频
    
    Args:
        keywords: 搜索关键词列表
        max_results: 最多返回的结果数量
        
    Returns:
        包含视频链接的列表
    """
    # 构建主要关键词搜索URL (使用所有关键词)
    combined_keyword = ' '.join(keywords)
    search_url = f"https://www.youtube.com/results?search_query={'+'.join(combined_keyword.split())}"
    
    # 发送请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"正在搜索同时包含关键词 '{combined_keyword}' 的YouTube视频...")
    
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        # 解析页面内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取视频ID和标题
        video_data = []
        
        # 提取视频ID
        video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
        unique_ids = []
        
        # 去重
        for vid in video_ids:
            if vid not in unique_ids:
                unique_ids.append(vid)
        
        # 对每个视频获取更多信息，验证是否包含所有关键词
        filtered_video_links = []
        count = 0
        
        print(f"正在验证视频是否包含所有关键词...")
        for vid in unique_ids:
            if count >= max_results:
                break
                
            video_url = f"https://www.youtube.com/watch?v={vid}"
            
            try:
                # 获取视频页面
                video_response = requests.get(video_url, headers=headers)
                video_response.raise_for_status()
                
                # 检查是否包含所有关键词
                all_keywords_found = True
                for keyword in keywords:
                    if keyword.lower() not in video_response.text.lower():
                        all_keywords_found = False
                        break
                
                if all_keywords_found:
                    filtered_video_links.append(video_url)
                    count += 1
                    print(f"找到符合条件的视频: {video_url}")
            
            except requests.exceptions.RequestException:
                # 跳过出错的视频
                continue
        
        return filtered_video_links
    
    except requests.exceptions.RequestException as e:
        print(f"搜索时出错: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='搜索YouTube和抖音视频并保存链接')
    parser.add_argument('--keywords-file', default='keywords.txt', help='关键词文件路径 (默认: keywords.txt)')
    parser.add_argument('--limit', type=int, help='每次最多添加的新链接数量 (将覆盖配置文件中的设置)')
    parser.add_argument('--output', default='videos.txt', help='输出文件路径 (默认: videos.txt)')
    parser.add_argument('--platform', choices=['youtube', 'douyin', 'all'], default='youtube', 
                        help='搜索平台 (默认: youtube，可选: youtube, douyin, all)')
    
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
    all_links = []
    
    if args.platform in ['youtube', 'all']:
        youtube_links = search_videos(keywords, 'youtube', limit * 2)
        print(f"YouTube搜索找到 {len(youtube_links)} 个视频")
        all_links.extend(youtube_links)
    
    if args.platform in ['douyin', 'all']:
        douyin_links = search_videos(keywords, 'douyin', limit * 2)
        print(f"抖音搜索找到 {len(douyin_links)} 个视频")
        all_links.extend(douyin_links)
    
    # 过滤掉已存在的链接
    new_links = [link for link in all_links if link not in existing_links]
    
    # 限制数量
    new_links = new_links[:limit]
    
    # 保存新链接
    if new_links:
        save_links(args.output, new_links)
        print(f"已添加 {len(new_links)} 个新链接到 {args.output}")
    else:
        print("未找到新链接")
    
if __name__ == "__main__":
    main() 