#!/bin/bash

# YouTube视频搜索和转录工具一键运行脚本

# 定义颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查Python安装
echo -e "${BLUE}检查Python安装...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到Python 3. 请安装Python 3后再试.${NC}"
    exit 1
fi

# 显示欢迎信息
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}YouTube视频搜索和转录工具${NC}"
echo -e "${GREEN}=================================${NC}"

# 检查依赖
echo -e "${BLUE}检查依赖...${NC}"
if ! python3 -c "import sys; sys.exit(0 if all(map(__import__, ['requests', 'bs4'])) else 1)" 2> /dev/null; then
    echo -e "${YELLOW}安装必要依赖...${NC}"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}依赖安装失败. 请检查网络连接和pip配置.${NC}"
        exit 1
    fi
fi

# 确保关键字文件存在
if [ ! -f "keywords.txt" ]; then
    echo -e "${YELLOW}未找到关键字文件，创建默认文件...${NC}"
    echo -e "紫微斗数,八字\n20" > keywords.txt
    echo -e "${GREEN}已创建关键字文件 keywords.txt，默认包含：${NC}"
    echo -e "${GREEN}第一行 - 关键字：紫微斗数,八字${NC}"
    echo -e "${GREEN}第二行 - 视频数量：20${NC}"
fi

# 显示当前配置
function show_current_config() {
    echo -e "${BLUE}当前配置:${NC}"
    
    if [ -f "keywords.txt" ]; then
        # 读取关键字（第一行）
        keywords=$(head -n 1 keywords.txt)
        echo -e "${GREEN}关键字: ${keywords}${NC}"
        
        # 读取视频数量（第二行）
        video_limit=$(sed -n '2p' keywords.txt 2>/dev/null)
        if [[ -z "$video_limit" || ! "$video_limit" =~ ^[0-9]+$ ]]; then
            echo -e "${YELLOW}视频数量未指定或无效，将使用默认值: 20${NC}"
            video_limit=20
        fi
        echo -e "${GREEN}每次抓取视频数量: ${video_limit}${NC}"
    else
        echo -e "${RED}未找到配置文件${NC}"
    fi
}

# 管理关键字
function manage_keywords() {
    show_current_config
    echo ""
    echo -e "${YELLOW}请选择操作:${NC}"
    echo -e "1) ${GREEN}修改关键字${NC}"
    echo -e "2) ${GREEN}修改视频数量${NC}"
    echo -e "3) ${GREEN}同时修改关键字和视频数量${NC}"
    echo -e "4) ${GREEN}返回主菜单${NC}"
    
    read -p "请输入选项 [1-4]: " kw_option
    
    case $kw_option in
        1)
            read -p "请输入新的关键字(多个关键字用逗号分隔): " new_keywords
            
            # 保留第二行（视频数量）
            video_limit=$(sed -n '2p' keywords.txt 2>/dev/null)
            if [[ -z "$video_limit" || ! "$video_limit" =~ ^[0-9]+$ ]]; then
                video_limit=20
            fi
            
            # 更新文件
            echo -e "${new_keywords}\n${video_limit}" > keywords.txt
            echo -e "${GREEN}已更新关键字${NC}"
            show_current_config
            ;;
        2)
            read -p "请输入每次抓取的视频数量: " new_limit
            
            # 验证输入是数字
            if [[ ! "$new_limit" =~ ^[0-9]+$ ]]; then
                echo -e "${RED}输入无效，必须是正整数${NC}"
                return
            fi
            
            # 保留第一行（关键字）
            keywords=$(head -n 1 keywords.txt)
            if [ -z "$keywords" ]; then
                keywords="紫微斗数,八字"
            fi
            
            # 更新文件
            echo -e "${keywords}\n${new_limit}" > keywords.txt
            echo -e "${GREEN}已更新视频数量${NC}"
            show_current_config
            ;;
        3)
            read -p "请输入新的关键字(多个关键字用逗号分隔): " new_keywords
            read -p "请输入每次抓取的视频数量: " new_limit
            
            # 验证输入是数字
            if [[ ! "$new_limit" =~ ^[0-9]+$ ]]; then
                echo -e "${RED}视频数量无效，必须是正整数，将使用默认值: 20${NC}"
                new_limit=20
            fi
            
            # 更新文件
            echo -e "${new_keywords}\n${new_limit}" > keywords.txt
            echo -e "${GREEN}已更新配置${NC}"
            show_current_config
            ;;
        4)
            return
            ;;
        *)
            echo -e "${RED}无效选项，返回主菜单${NC}"
            return
            ;;
    esac
}

# 显示选项菜单
while true; do
    echo -e "\n${BLUE}请选择操作:${NC}"
    echo -e "1) ${GREEN}一键搜索和转录${NC}"
    echo -e "2) ${GREEN}仅搜索视频${NC}"
    echo -e "3) ${GREEN}仅转录现有视频${NC}"
    echo -e "4) ${GREEN}高级搜索${NC} (使用Selenium，需要Chrome浏览器)"
    echo -e "5) ${GREEN}管理配置${NC}"
    echo -e "6) ${GREEN}显示当前配置${NC}"
    echo -e "7) ${GREEN}退出${NC}"

    read -p "请输入选项 [1-7]: " option

    case $option in
        1)
            echo -e "${GREEN}执行一键搜索和转录...${NC}"
            python3 auto_search_and_transcribe.py
            ;;
        2)
            echo -e "${GREEN}仅搜索视频...${NC}"
            python3 search_youtube_videos.py
            ;;
        3)
            echo -e "${GREEN}仅转录现有视频...${NC}"
            python3 youtube_transcription.py
            ;;
        4)
            echo -e "${GREEN}使用Selenium进行高级搜索...${NC}"
            python3 advanced_search.py
            ;;
        5)
            manage_keywords
            ;;
        6)
            show_current_config
            ;;
        7)
            echo -e "${BLUE}退出程序${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}无效选项，请重新选择${NC}"
            ;;
    esac
    
    # 如果不是在管理配置，询问用户是否继续
    if [ "$option" != "5" ] && [ "$option" != "6" ]; then
        read -p "按回车键继续..." continue_key
    fi
done 