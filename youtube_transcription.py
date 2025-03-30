#!/usr/bin/env python3
import os
import re
import time
import requests
import subprocess
import json

# 你需要在这里设置你的AssemblyAI API密钥
# 注册地址：https://www.assemblyai.com/ (有免费额度)
ASSEMBLYAI_API_KEY = "a86179f5b73045fb878609759958081e"  # 替换为你的API密钥

# DeepSeek API密钥
DEEPSEEK_API_KEY = "sk-b4d8ce9a5fe6429da61e1aba29219edd"

# 输出目录
OUTPUT_DIR = "output"

def get_video_links():
    """从videos.txt文件中读取视频链接"""
    with open('videos.txt', 'r') as file:
        # 移除行尾空白和空行
        links = [line.strip() for line in file.readlines() if line.strip()]
    return links

def clean_filename(title):
    """清理文件名，替换不合法字符"""
    return re.sub(r'[\\/*?:"<>|]', '_', title)

def identify_platform(link):
    """识别链接来自哪个平台"""
    if 'youtube.com' in link or 'youtu.be' in link:
        return 'youtube'
    elif 'douyin.com' in link or 'tiktok.com' in link or 'iesdouyin.com' in link:
        return 'douyin'
    else:
        return 'unknown'

def download_audio(link, output_dir):
    """下载视频的音频部分，支持YouTube和抖音"""
    try:
        print(f"正在获取视频信息: {link}")
        
        # 识别视频平台
        platform = identify_platform(link)
        if platform == 'unknown':
            print(f"警告: 未知的视频平台链接: {link}")
            print("目前仅支持YouTube和抖音链接")
            return None, None
        
        print(f"识别为{platform}视频链接")
        
        # 获取视频标题
        result = subprocess.run(
            ['yt-dlp', '--print', 'title', '--no-playlist', link],
            capture_output=True, text=True, check=True
        )
        title = result.stdout.strip()
        title = clean_filename(title)
        print(f"视频标题: {title}")
        
        # 设置输出文件名
        output_file = os.path.join(output_dir, f"{title}.mp3")
        
        # 使用yt-dlp下载仅音频并转换为mp3
        print(f"正在下载音频...")
        
        # 对于抖音，可能需要添加额外的选项以处理重定向
        cmd = [
            'yt-dlp',
            '-x',  # 提取音频
            '--audio-format', 'mp3',  # 转换为mp3
            '--audio-quality', '0',  # 最佳质量
            '-o', output_file,
            '--no-playlist',  # 不下载播放列表中的其他视频
        ]
        
        # 针对抖音添加特殊处理参数
        if platform == 'douyin':
            cmd.extend(['--referer', 'https://www.douyin.com/'])
        
        cmd.append(link)  # 添加链接
        
        subprocess.run(cmd, check=True)
        
        print(f"音频下载完成: {output_file}")
        return output_file, title
    except subprocess.CalledProcessError as e:
        print(f"下载视频音频时出错 (命令执行失败): {e}")
        print(f"错误输出: {e.stderr}")
        return None, None
    except Exception as e:
        print(f"下载视频音频时出错: {e}")
        return None, None

def transcribe_with_assemblyai(audio_file):
    """使用AssemblyAI转录音频文件"""
    if not ASSEMBLYAI_API_KEY:
        print("错误: 请设置你的AssemblyAI API密钥")
        return None
    
    headers = {
        "authorization": ASSEMBLYAI_API_KEY,
        "content-type": "application/json"
    }
    
    try:
        print(f"正在上传音频文件到AssemblyAI...")
        
        # 上传音频文件
        with open(audio_file, "rb") as f:
            response = requests.post(
                "https://api.assemblyai.com/v2/upload",
                headers=headers,
                data=f
            )
        
        if response.status_code != 200:
            print(f"上传失败: {response.text}")
            return None
            
        upload_url = response.json()["upload_url"]
        
        # 开始转录
        print("开始转录...")
        response = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            headers=headers,
            json={
                "audio_url": upload_url,
                "language_code": "zh",  # 指定中文语言
                "punctuate": True,      # 添加标点符号
                "format_text": True     # 格式化文本
            }
        )
        
        transcript_id = response.json()["id"]
        polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        
        # 等待转录完成
        while True:
            response = requests.get(polling_endpoint, headers=headers)
            status = response.json()["status"]
            
            if status == "completed":
                print("转录完成!")
                return response.json()["text"]
            elif status == "error":
                print(f"转录出错: {response.json()['error']}")
                return None
            else:
                print(f"转录进行中... 状态: {status}")
                time.sleep(10)  # 等待10秒后再次检查
                
    except Exception as e:
        print(f"转录过程中出错: {e}")
        return None

def format_text_with_deepseek(text):
    """使用DeepSeek API对文本进行格式化，添加标点符号"""
    if not DEEPSEEK_API_KEY:
        print("警告: 未设置DeepSeek API密钥，跳过文本格式化")
        return text
    
    print("使用DeepSeek添加标点符号和格式化文本...")
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        payload = {
            "model": "deepseek-chat", 
            "messages": [
                {
                    "role": "system", 
                    "content": "你是一位精通中文的专家，负责为文本添加适当的标点符号，使文本更易阅读。保持原始内容不变，只添加必要的标点符号。"
                },
                {
                    "role": "user", 
                    "content": f"请为以下文本添加适当的标点符号，使其更易阅读。请保持原始内容不变，只添加必要的标点符号：\n\n{text}"
                }
            ],
            "temperature": 0.1,
            "top_p": 0.8,
            "max_tokens": 8000
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            formatted_text = response.json()["choices"][0]["message"]["content"]
            print("文本格式化完成")
            return formatted_text
        else:
            print(f"DeepSeek API请求失败: {response.text}")
            return text
    
    except Exception as e:
        print(f"使用DeepSeek格式化文本时出错: {e}")
        return text

def save_to_markdown(transcript, title):
    """将转录内容保存为Markdown文件"""
    if not transcript:
        return None
        
    # 创建安全的文件名
    safe_title = clean_filename(title)
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 在输出目录中创建Markdown文件
    md_file = os.path.join(OUTPUT_DIR, f"{safe_title}.md")
    
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(transcript)
    
    print(f"已创建Markdown文件: {md_file}")
    return md_file

def main():
    # 如果未设置API密钥，提示用户
    if not ASSEMBLYAI_API_KEY:
        print("警告: 未设置AssemblyAI API密钥。请编辑脚本设置你的API密钥。")
        print("注册地址: https://www.assemblyai.com/ (有免费额度)")
        return
    
    # 创建临时目录存放音频文件
    temp_dir = "temp_audio"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    links = get_video_links()
    print(f"找到 {len(links)} 个视频链接")
    
    # 按平台分类链接
    youtube_links = []
    douyin_links = []
    unknown_links = []
    
    for link in links:
        platform = identify_platform(link)
        if platform == 'youtube':
            youtube_links.append(link)
        elif platform == 'douyin':
            douyin_links.append(link)
        else:
            unknown_links.append(link)
    
    print(f"YouTube链接: {len(youtube_links)}个")
    print(f"抖音链接: {len(douyin_links)}个")
    if unknown_links:
        print(f"未知平台链接: {len(unknown_links)}个 (这些链接将被跳过)")
    
    # 处理所有有效链接
    valid_links = youtube_links + douyin_links
    
    for i, link in enumerate(valid_links, 1):
        print(f"\n处理视频 {i}/{len(valid_links)}: {link}")
        
        # 下载音频
        audio_file, title = download_audio(link, temp_dir)
        if not audio_file or not title:
            print(f"跳过转录，无法下载: {link}")
            continue
        
        # 转录音频
        transcript = transcribe_with_assemblyai(audio_file)
        if not transcript:
            print(f"转录失败: {audio_file}")
            continue
        
        # 使用DeepSeek添加标点符号
        formatted_transcript = format_text_with_deepseek(transcript)
        
        # 保存为Markdown
        md_file = save_to_markdown(formatted_transcript, title)
        
        # 清理音频文件节省空间
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"已删除临时音频文件: {audio_file}")
    
    # 清理临时目录
    if os.path.exists(temp_dir) and not os.listdir(temp_dir):
        os.rmdir(temp_dir)
    
    print("\n所有视频处理完成!")
    print(f"转录结果已保存到 {OUTPUT_DIR} 目录")

if __name__ == "__main__":
    main() 