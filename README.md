   ```bash
如何使用:

安装 psutil 库:
如果你还没有安装 psutil，需要先安装它。在你的终端或命令行中运行：


pip install psutil
# 或者使用 pip3
# pip3 install psutil
保存脚本:
将上面的代码保存到一个 .py 文件中，例如 server_check.py。

运行脚本:

将脚本文件上传到你需要巡检的每一台服务器上。
在服务器的终端中，使用 Python 解释器运行脚本：


python server_check.py
# 或者如果你的系统默认是Python 2，而你安装了Python 3
# python3 server_check.py
注意: 获取某些进程信息（特别是路径）可能需要 root 或管理员权限。如果遇到权限错误（AccessDenied 或 PermissionError），尝试使用 sudo 运行：


sudo python server_check.py
# 或者
# sudo python3 server_check.py
