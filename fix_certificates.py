#!/usr/bin/env python3
import os
import ssl
import certifi
import subprocess

print("开始修复SSL证书配置...\n")

# 打印当前使用的证书路径
print(f"当前证书路径: {certifi.where()}")

# 尝试更新pip和certifi
try:
    subprocess.run(["pip", "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)
    subprocess.run(["pip", "install", "--upgrade", "certifi"], check=True)
    print("\n已更新pip和certifi包")
except Exception as e:
    print(f"\n更新pip和certifi时出错: {e}")

# 设置SSL环境变量
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

print("\n已设置以下环境变量:")
print(f"SSL_CERT_FILE={certifi.where()}")
print(f"REQUESTS_CA_BUNDLE={certifi.where()}")

# 测试SSL连接
print("\n正在测试与PyPI的SSL连接...")
try:
    import urllib.request
    urllib.request.urlopen("https://pypi.org").read()
    print("成功连接到PyPI! SSL证书配置正常。")
except Exception as e:
    print(f"连接PyPI时出错: {e}")
    print("\n仍然存在SSL问题，请尝试以下命令来安装依赖:")
    print("pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt")

print("\n请尝试正常安装requirements.txt:")
print("pip install -r requirements.txt") 