# Markdown4Zhihu

这是一个可以将您的 Markdown 文件一键转换为知乎编辑器支持模式的仓库。

- 它会自动的处理**图片，行内公式，多行公式**，以及 **表格** 的格式。
- 当图片过大时，您可以选择加上 `--compress` 选项，对超过大小阈值（这里约为500K）的图片进行 **自动压缩**。
- 自动将笔记与 GitHub 或 Gitee 仓库同步，支持 **自定义仓库名、用户名、分支名等字段**
- 根据 Markdown 中图片的本地相对链接 **生成 URL** 并转换

## 使用方法

1. 首先，为您的笔记建立 Git 本地和远程仓库
2. 将脚本 `zhihu-publisher.py` 下载到仓库根目录（与 `.git` 同级）
3. 确保本机已安装 [Python 3](https://www.python.org/)
4. 命令行输入：

```
virtualenv -p=python3.10 venv
source venv/bin/activate
pip install -r requirements.txt
```

5. 查看如何使用:

```
python zhihu-publisher.py --help
```
