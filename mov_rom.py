"""
ROM文件同步工具

这个脚本用于同步和比较两个目录之间的ROM文件。主要功能包括：
1. 将源目录中的ROM文件复制到目标目录
2. 检查并移除目标目录中不存在于源目录的文件
3. 比较文件大小，如果大小不同则更新文件
4. 将需要更新的文件移动到rmv子目录

作者: Jason Yu
"""

import os
import shutil


# 源目录和目标目录的路径
SRC_PATH = r"D:\jasonyu\Downloads\MAME 0.277 ROMs (merged)"
DST_PATH = r"F:\ROMS"


def format_file_size(file_size):
    """将文件大小（字节）转换为人类可读的格式（B/KB/MB/GB）。"""
    if file_size < 1024:
        return f"{file_size:.2f}B"
    elif file_size < 1024 * 1024:
        return f"{file_size / 1024:.2f}KB"
    elif file_size < 1024 * 1024 * 1024:
        return f"{file_size / (1024 * 1024):.2f}MB"
    else:
        return f"{file_size / (1024 * 1024 * 1024):.2f}GB"


def main():
    # 获取源目录中的所有文件列表，并移除.fdmdownload后缀
    file_list = os.listdir(SRC_PATH)
    file_list = [file.replace(".fdmdownload", "") for file in file_list]
    file_list = set(file_list)

    # 检查目标目录中需要移除的文件
    rmv_list = []
    for file in os.listdir(DST_PATH):
        if os.path.isdir(os.path.join(DST_PATH, file)):
            continue
        if file not in file_list:
            rmv_list.append(file)

    # 如果存在需要移除的文件，将它们移动到rmv子目录
    if rmv_list:
        print(len(rmv_list))
        print(rmv_list[:10])  # 打印前10个要移除的文件
        print(rmv_list[-10:])  # 打印后10个要移除的文件
        os.makedirs(os.path.join(DST_PATH, "rmv"), exist_ok=True)
        for file in rmv_list:
            shutil.move(os.path.join(DST_PATH, file), os.path.join(DST_PATH, "rmv", file))

    rmv_list = []
    file_size = 0
    for file in os.listdir(os.path.join(DST_PATH, "rmv")):
        if file not in file_list:
            rmv_list.append(file)
            file_size += os.path.getsize(os.path.join(DST_PATH, "rmv", file))

    file_size = format_file_size(file_size)
    print(f"Total {len(rmv_list)} files {file_size} files are not in src_path")

    # 获取目标目录中的所有zip文件
    file_list = os.listdir(DST_PATH)
    file_list = [file for file in file_list if file.endswith(".zip")]
    file_list = set(file_list)

    # 同步源目录中的文件到目标目录

    cnt = 0
    file_size = 0

    for file in os.listdir(SRC_PATH):
        if not file.endswith(".zip"):
            continue
        src_file_path = os.path.join(SRC_PATH, file)
        dst_file_path = os.path.join(DST_PATH, file)
        if file not in file_list:
            print(f"{file} is not in dst_path,")
            print(f"copying {format_file_size(os.path.getsize(src_file_path))}", end=" ")
            shutil.copy(src_file_path, dst_file_path)
            cnt += 1
            file_size += os.path.getsize(src_file_path)
        elif os.path.getsize(src_file_path) == os.path.getsize(dst_file_path):
            # print(f"{file} is in dst_path and size is the same")
            continue
        else:
            print(f"{file} is in dst_path but size is different,")
            print(f"copying {format_file_size(os.path.getsize(src_file_path))}", end=" ")
            shutil.move(dst_file_path, os.path.join(DST_PATH, "rmv", file))
            shutil.copy(src_file_path, dst_file_path)
            cnt += 1
            file_size += os.path.getsize(src_file_path)
        print(f"{format_file_size(file_size)} copied")
        if cnt % 1000 == 0:
            print(f"Processed {cnt} files")

    file_size = format_file_size(file_size)

    print(f"Total {cnt} files processed, {file_size} processed")

    # 获取rmv目录中的所有zip文件
    file_list = os.listdir(os.path.join(DST_PATH, "rmv"))
    file_list = [file for file in file_list if file.endswith(".zip")]
    file_list = set(file_list)

    # 检查新添加的文件
    new_file_list = []
    file_size = 0
    for file in os.listdir(DST_PATH):
        if os.path.isdir(os.path.join(DST_PATH, file)):
            continue
        if file in file_list:
            new_file_list.append(file)
            file_size += os.path.getsize(os.path.join(DST_PATH, file))
    new_file_list.sort()
    file_size = format_file_size(file_size)

    # 打印新添加的文件统计信息
    print(f"Total {len(new_file_list)} files  {file_size} are new")
    print(new_file_list[:10])  # 打印前10个新文件
    print(new_file_list[-10:])  # 打印后10个新文件

    file_size = 0
    cnt = 0
    for file in os.listdir(DST_PATH):
        if os.path.isdir(os.path.join(DST_PATH, file)):
            continue
        file_size += os.path.getsize(os.path.join(DST_PATH, file))
        cnt += 1

    file_size = format_file_size(file_size)
    print(f"Total {cnt} files in {DST_PATH}, {file_size}")

    file_size = 0
    cnt = 0
    for file in os.listdir(SRC_PATH):
        if file.endswith(".fdmdownload"):
            file_size += os.path.getsize(os.path.join(SRC_PATH, file))
            cnt += 1

    file_size = format_file_size(file_size)
    print(f"Total {cnt} files in {SRC_PATH} are still downloading, {file_size} left")


if __name__ == "__main__":
    main()
