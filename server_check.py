#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psutil
import socket
import datetime
import os

# --- 辅助函数：将字节转换为GB ---
def bytes_to_gb(bytes_val):
    """将字节大小转换为GB，保留两位小数"""
    try:
        gb_val = round(bytes_val / (1024**3), 2)
        return gb_val
    except TypeError:
        return "N/A"

# --- 信息获取函数 ---

def get_hostname_ip():
    """获取主机名和IP地址"""
    hostname = socket.gethostname()
    ip_addresses = []
    try:
        # 获取所有网络接口的地址信息
        all_addrs = psutil.net_if_addrs()
        for interface_name, snicaddr_list in all_addrs.items():
            # 通常忽略本地回环地址
            if interface_name == 'lo':
                continue
            for snicaddr in snicaddr_list:
                # 筛选IPv4地址
                if snicaddr.family == socket.AF_INET:
                    ip_addresses.append(snicaddr.address)
        # 去重并排序（如果需要）
        ip_addresses = sorted(list(set(ip_addresses)))
    except Exception as e:
        print(f"获取IP地址时出错: {e}")
        ip_addresses.append("获取失败")
    return hostname, ip_addresses

def get_cpu_info():
    """获取CPU使用率"""
    # interval=1 表示统计1秒内的CPU使用率，更准确
    cpu_percent = psutil.cpu_percent(interval=1)
    # cpu_count = psutil.cpu_count(logical=False) # 物理核心数
    # logical_cpu_count = psutil.cpu_count(logical=True) # 逻辑核心数
    return cpu_percent

def get_memory_info():
    """获取内存信息 (总量, 使用量, 使用率, 剩余量) GB"""
    mem = psutil.virtual_memory()
    mem_total_gb = bytes_to_gb(mem.total)
    mem_used_gb = bytes_to_gb(mem.used)
    mem_free_gb = bytes_to_gb(mem.free) # 或者用 available 更准确些
    mem_available_gb = bytes_to_gb(mem.available)
    mem_percent = mem.percent
    # 返回 总量, 使用量, 使用率, 可用量(通常比free更代表实际可用)
    return mem_total_gb, mem_used_gb, mem_percent, mem_available_gb

def get_disk_info():
    """获取所有磁盘分区信息 (挂载点, 总量, 使用量, 使用率, 剩余量) GB"""
    disk_info_list = []
    try:
        partitions = psutil.disk_partitions()
        for partition in partitions:
            mountpoint = partition.mountpoint
            try:
                usage = psutil.disk_usage(mountpoint)
                disk_total_gb = bytes_to_gb(usage.total)
                disk_used_gb = bytes_to_gb(usage.used)
                disk_free_gb = bytes_to_gb(usage.free)
                disk_percent = usage.percent
                disk_info_list.append({
                    "mountpoint": mountpoint,
                    "total_gb": disk_total_gb,
                    "used_gb": disk_used_gb,
                    "free_gb": disk_free_gb,
                    "percent": disk_percent,
                    "fstype": partition.fstype # 文件系统类型
                })
            except PermissionError:
                print(f"权限不足，无法读取磁盘信息: {mountpoint}")
                disk_info_list.append({
                    "mountpoint": mountpoint,
                    "error": "Permission Denied"
                })
            except Exception as e:
                print(f"读取磁盘信息时出错 ({mountpoint}): {e}")
                disk_info_list.append({
                    "mountpoint": mountpoint,
                    "error": str(e)
                })
    except Exception as e:
        print(f"获取磁盘分区列表时出错: {e}")
    return disk_info_list

def get_process_info():
    """获取进程信息 (PID, 进程名, 进程路径)"""
    process_list = []
    # 迭代所有进程，尝试获取'pid', 'name', 'exe'信息
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            proc_info = proc.info
            pid = proc_info['pid']
            name = proc_info['name']
            # 尝试获取可执行文件路径，如果失败，尝试获取命令行
            path = proc_info['exe'] if proc_info['exe'] else ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else 'N/A'

            # 处理路径为空或权限问题
            if not path or path == 'N/A':
                 # 对于某些系统进程或内核线程，可能无法获取路径
                 path = f"[无法获取路径或内核线程: {name}]"
            elif not os.path.isabs(path) and path != 'N/A' and not path.startswith('['): # 如果不是绝对路径且看起来不像特殊标记
                 # 尝试基于命令行找到可能的路径 (这只是一个猜测)
                 if proc_info['cmdline'] and os.path.isabs(proc_info['cmdline'][0]):
                      path = proc_info['cmdline'][0]

            process_list.append({
                "pid": pid,
                "name": name,
                "path": path
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # 忽略已经结束、无权限访问或僵尸进程
            pass
        except Exception as e:
            print(f"获取进程 {getattr(proc, 'pid', 'N/A')} 信息时出错: {e}")
    return process_list

# --- 主程序 ---
if __name__ == "__main__":
    print("=" * 40)
    print(f"服务器巡检报告 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 40)

    # 1. 主机名和IP
    hostname, ip_addresses = get_hostname_ip()
    print("\n--- [基本信息] ---")
    print(f"主机名 (Hostname): {hostname}")
    print(f"IP 地址 (IP Addresses): {', '.join(ip_addresses)}")

    # 2. CPU 信息
    cpu_usage = get_cpu_info()
    print("\n--- [CPU 信息] ---")
    print(f"CPU 使用率 (CPU Usage): {cpu_usage}%")

    # 3. 内存信息
    mem_total, mem_used, mem_percent, mem_available = get_memory_info()
    print("\n--- [内存信息 (Memory)] ---")
    print(f"  总量 (Total): {mem_total} GB")
    print(f"  已用 (Used): {mem_used} GB")
    print(f"  可用 (Available): {mem_available} GB")
    print(f"  使用率 (Usage Rate): {mem_percent}%")

    # 4. 磁盘信息
    disks = get_disk_info()
    print("\n--- [磁盘信息 (Disk Usage)] ---")
    if disks:
        # 打印表头
        print(f"{'挂载点 (Mount Point)':<25} {'文件系统 (FS Type)':<15} {'总量 (Total GB)':<15} {'已用 (Used GB)':<15} {'剩余 (Free GB)':<15} {'使用率 (Use %)'}")
        print("-" * 95)
        for disk in disks:
            if "error" not in disk:
                print(f"{disk['mountpoint']:<25} {disk['fstype']:<15} {disk['total_gb']:<15.2f} {disk['used_gb']:<15.2f} {disk['free_gb']:<15.2f} {disk['percent']}%")
            else:
                print(f"{disk['mountpoint']:<25} {'N/A':<15} {'N/A':<15} {'N/A':<15} {'N/A':<15} {disk['error']}")
    else:
        print("未能获取到磁盘信息。")


    # 5. 进程信息
    processes = get_process_info()
    print("\n--- [进程信息 (Running Processes)] ---")
    if processes:
        # 打印表头
        print(f"{'PID':<10} {'进程名 (Name)':<30} {'进程路径/命令 (Path/Command)'}")
        print("-" * 80)
        for proc in processes:
            # 限制路径显示长度，避免过长
            path_display = proc['path'] if len(proc['path']) < 100 else proc['path'][:97] + '...'
            print(f"{proc['pid']:<10} {proc['name']:<30} {path_display}")
        print(f"\n总进程数 (Total Processes): {len(processes)}")
    else:
        print("未能获取到进程信息。")

    print("\n" + "=" * 40)
    print("巡检完成。")
    print("=" * 40)