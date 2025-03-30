#!/usr/bin/env python3
"""
自动搜索并转录YouTube视频

此脚本自动执行以下步骤：
1. 从keywords.txt读取关键词和视频数量配置
2. 搜索YouTube视频
3. 将新链接保存到videos.txt
4. 转录这些新链接的视频内容
"""

import os
import sys
import argparse
import subprocess

def read_keywords_config(file_path):
    """
    从文件中读取关键词和配置信息
    
    Args:
        file_path: 关键词文件的路径
        
    Returns:
        包含关键词列表和视频数量的元组 (keywords_file_exists, limit)
    """
    limit = 20
    
    if not os.path.exists(file_path):
        return False, limit
    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        
        # 读取第二行视频数量
        if len(lines) > 1 and lines[1].strip():
            try:
                limit = int(lines[1].strip())
                if limit <= 0:
                    limit = 20
            except ValueError:
                limit = 20
    
    return True, limit

def run_command(command):
    """
    运行命令并返回结果
    
    Args:
        command: 要运行的命令列表
        
    Returns:
        命令执行的退出码
    """
    print(f"执行: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")
        return e.returncode

def main():
    parser = argparse.ArgumentParser(description='自动搜索并转录YouTube视频')
    parser.add_argument('--keywords-file', default='keywords.txt', help='关键词文件路径 (默认: keywords.txt)')
    parser.add_argument('--limit', type=int, help='每次最多添加的新链接数量 (将覆盖配置文件中的设置)')
    parser.add_argument('--output', default='videos.txt', help='输出文件路径 (默认: videos.txt)')
    parser.add_argument('--use-selenium', action='store_true', help='使用Selenium进行搜索（更可靠但需要安装浏览器）')
    parser.add_argument('--skip-search', action='store_true', help='跳过搜索步骤，直接执行转录')
    parser.add_argument('--skip-transcribe', action='store_true', help='仅执行搜索步骤，不执行转录')
    
    args = parser.parse_args()
    
    # 读取配置文件中的视频数量
    _, config_limit = read_keywords_config(args.keywords_file)
    
    # 优先使用命令行参数的limit，如果没有则使用配置文件中的limit
    limit = args.limit if args.limit is not None else config_limit
    
    # 步骤1: 搜索视频
    if not args.skip_search:
        print("\n===== 步骤1: 搜索YouTube视频 =====")
        
        if args.use_selenium:
            search_script = "advanced_search.py"
        else:
            search_script = "search_youtube_videos.py"
        
        search_cmd = [
            sys.executable, search_script, 
            "--keywords-file", args.keywords_file
        ]
        
        # 仅当命令行指定了limit时，才将其传递给搜索脚本
        if args.limit is not None:
            search_cmd.extend(["--limit", str(args.limit)])
            
        search_cmd.extend(["--output", args.output])
        
        exit_code = run_command(search_cmd)
        if exit_code != 0:
            print("搜索步骤失败，退出程序")
            return exit_code
    
    # 步骤2: 转录视频
    if not args.skip_transcribe:
        print("\n===== 步骤2: 转录YouTube视频 =====")
        
        transcribe_cmd = [sys.executable, "youtube_transcription.py"]
        exit_code = run_command(transcribe_cmd)
        if exit_code != 0:
            print("转录步骤失败")
            return exit_code
    
    print("\n===== 全部任务完成 =====")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 