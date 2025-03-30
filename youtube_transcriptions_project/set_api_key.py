#!/usr/bin/env python3
import os
import re

def set_api_key():
    """设置AssemblyAI API密钥到youtube_transcription.py文件中"""
    print("=" * 60)
    print("设置AssemblyAI API密钥")
    print("=" * 60)
    print("请先在 https://www.assemblyai.com/ 注册账号并获取API密钥")
    print("注册后，您可以在控制面板中找到您的API密钥")
    print("=" * 60)
    
    # 获取用户输入的API密钥
    api_key = input("请输入您的AssemblyAI API密钥: ").strip()
    
    if not api_key:
        print("错误: API密钥不能为空")
        return False
    
    try:
        # 读取原始文件内容
        with open('youtube_transcription.py', 'r') as file:
            content = file.read()
        
        # 替换API密钥
        new_content = re.sub(
            r'ASSEMBLYAI_API_KEY = ".*?"',
            f'ASSEMBLYAI_API_KEY = "{api_key}"',
            content
        )
        
        # 写入更新后的内容
        with open('youtube_transcription.py', 'w') as file:
            file.write(new_content)
        
        print("\n成功设置API密钥!")
        print("现在您可以运行 python3 youtube_transcription.py 开始转录视频")
        return True
    
    except Exception as e:
        print(f"设置API密钥时出错: {e}")
        return False

if __name__ == "__main__":
    set_api_key() 