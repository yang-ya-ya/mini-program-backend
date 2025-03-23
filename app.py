from flask import Flask, request, jsonify
import base64
import requests
import os
import time

app = Flask(__name__)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # 从环境变量读取
REPO_OWNER = "yang-ya-ya"              # 替换为你的GitHub用户名
REPO_NAME = "image-storage"               # 仓库名
BRANCH = "main"                           # 分支名

@app.route('/upload', methods=['POST'])
def upload():
    # 1. 获取用户身份和文件
    openid = request.headers.get('X-OpenID')
    file = request.files['file']
    file_content = file.read()
    
    # 2. 生成唯一文件名（避免重复）
    file_extension = file.filename.split('.')[-1]
    file_name = f"images/{openid}_{int(time.time())}.{file_extension}"
    
    # 3. 上传到GitHub
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "User-Agent": "MiniProgram-Upload"
    }
    data = {
        "message": f"Upload by {openid}",
        "content": base64.b64encode(file_content).decode('utf-8'),
        "branch": BRANCH
    }
    response = requests.put(url, json=data, headers=headers)
    
    # 4. 返回CDN链接
    if response.status_code == 201:
        cdn_url = f"https://cdn.jsdelivr.net/gh/{REPO_OWNER}/{REPO_NAME}@{BRANCH}/{file_name}"
        return jsonify({"success": True, "url": cdn_url})
    else:
        return jsonify({"success": False, "error": "上传失败，请检查Token和仓库权限"})

if __name__ == '__main__':
    app.run()