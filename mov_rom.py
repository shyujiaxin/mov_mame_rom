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


def _get_processed_source_files(path):
    """获取源目录中的所有文件列表，并移除.fdmdownload后缀。"""
    file_list = os.listdir(path)
    file_list = [file.replace(".fdmdownload", "") for file in file_list]
    return set(file_list)


def _handle_removals(source_file_list, dst_path):
    """检查目标目录中需要移除的文件，并将它们移动到rmv子目录。"""
    rmv_list = []
    for file in os.listdir(dst_path):
        if os.path.isdir(os.path.join(dst_path, file)):
            continue
        if file not in source_file_list:
            rmv_list.append(file)

    if rmv_list:
        print(len(rmv_list))
        print(rmv_list[:10])
        print(rmv_list[-10:])
        os.makedirs(os.path.join(dst_path, "rmv"), exist_ok=True)
        for file in rmv_list:
            shutil.move(os.path.join(dst_path, file), os.path.join(dst_path, "rmv", file))

    file_size = 0
    current_rmv_list = []
    rmv_dir_path = os.path.join(dst_path, "rmv")
    if os.path.exists(rmv_dir_path):
        for file in os.listdir(rmv_dir_path):
            if file not in source_file_list:
                current_rmv_list.append(file)
                file_size += os.path.getsize(os.path.join(rmv_dir_path, file))

    file_size_formatted = format_file_size(file_size)
    print(f"Total {len(current_rmv_list)} files {file_size_formatted} files are not in src_path")


def _synchronize_files(src_path, dst_path, dst_zip_files):
    """同步源目录中的zip文件到目标目录。"""
    cnt = 0
    file_size_total = 0

    for file in os.listdir(src_path):
        if not file.endswith(".zip"):
            continue
        src_file_path = os.path.join(src_path, file)
        dst_file_path = os.path.join(dst_path, file)
        if file not in dst_zip_files:
            print(f"{file} is not in dst_path,")
            print(f"copying {format_file_size(os.path.getsize(src_file_path))}", end=" ")
            shutil.copy(src_file_path, dst_file_path)
            cnt += 1
            file_size_total += os.path.getsize(src_file_path)
        elif os.path.getsize(src_file_path) == os.path.getsize(dst_file_path):
            continue
        else:
            print(f"{file} is in dst_path but size is different,")
            print(f"copying {format_file_size(os.path.getsize(src_file_path))}", end=" ")
            shutil.move(dst_file_path, os.path.join(dst_path, "rmv", file))
            shutil.copy(src_file_path, dst_file_path)
            cnt += 1
            file_size_total += os.path.getsize(src_file_path)
        print(f"{format_file_size(file_size_total)} copied")
        if cnt % 1000 == 0:
            print(f"Processed {cnt} files")

    file_size_total_formatted = format_file_size(file_size_total)
    print(f"Total {cnt} files processed, {file_size_total_formatted} processed")


def _report_new_files(dst_path, rmv_zip_files):
    """检查并打印新添加的文件统计信息。"""
    new_file_list = []
    file_size = 0
    for file in os.listdir(dst_path):
        if os.path.isdir(os.path.join(dst_path, file)):
            continue
        if file in rmv_zip_files:
            new_file_list.append(file)
            file_size += os.path.getsize(os.path.join(dst_path, file))
    new_file_list.sort()
    file_size = format_file_size(file_size)

    print(f"Total {len(new_file_list)} files  {file_size} are new")
    print(new_file_list[:10])
    print(new_file_list[-10:])


def _summarize_directory_contents(path, description):
    """统计并打印指定目录的文件总数和总大小。"""
    file_size = 0
    cnt = 0
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            continue
        file_size += os.path.getsize(os.path.join(path, file))
        cnt += 1

    file_size = format_file_size(file_size)
    print(f"Total {cnt} files in {path}, {file_size}{description}")


def _report_downloading_files(src_path):
    """检查并打印源目录中仍在下载的文件统计信息。"""
    file_size = 0
    cnt = 0
    for file in os.listdir(src_path):
        if file.endswith(".fdmdownload"):
            file_size += os.path.getsize(os.path.join(src_path, file))
            cnt += 1

    file_size = format_file_size(file_size)
    print(f"Total {cnt} files in {src_path} are still downloading, {file_size} left")


def main():
    """主函数，用于协调ROM文件的同步和报告。"""
    source_file_list = _get_processed_source_files(SRC_PATH)

    _handle_removals(source_file_list, DST_PATH)

    # 获取目标目录中的所有zip文件
    file_list = os.listdir(DST_PATH)
    file_list = [file for file in file_list if file.endswith(".zip")]
    dst_zip_files = set(file_list)

    _synchronize_files(SRC_PATH, DST_PATH, dst_zip_files)

    # 获取rmv目录中的所有zip文件
    rmv_zip_files = os.listdir(os.path.join(DST_PATH, "rmv"))
    rmv_zip_files = [file for file in rmv_zip_files if file.endswith(".zip")]
    rmv_zip_files = set(rmv_zip_files)

    _report_new_files(DST_PATH, rmv_zip_files)

    _summarize_directory_contents(DST_PATH, "")

    _report_downloading_files(SRC_PATH)


if __name__ == "__main__":
    main()
