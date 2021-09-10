import datetime
import hashlib
import os
import time


def str_md5sum(my_str, cache_map):
    if cache_map.get(my_str, None) is not None:
        return cache_map.get(my_str, None)
    if not isinstance(my_str, str):
        raise TypeError
    m = hashlib.md5()
    m.update(my_str.encode("utf8"))
    result = m.hexdigest()
    cache_map[my_str] = result
    return result


def file_md5sum(path, cache_map):
    if cache_map.get(path, None) is not None:
        return cache_map.get(path, None)
    if not os.path.exists(path):
        raise ValueError()
    if os.path.isdir(path):
        raise TypeError()
    m = hashlib.md5()
    offset = 0
    f_size = os.path.getsize(path)
    block_size = 1024 * 1024
    with open(path, 'rb') as f:
        data = f.read(block_size)
        while len(data) > 0:
            m.update(data)
            if f_size // 5 > block_size:
                offset += f_size // 5
                f.seek(offset)
            data = f.read(block_size)
        if f_size // 5 > block_size:
            m.update(str(f_size).encode("utf8"))
    result = m.hexdigest()
    cache_map[path] = result
    # print(len(cache_map), path, result)
    return result


def dir_md5sum(path, cache_map):
    if cache_map.get(path, None) is not None:
        return cache_map.get(path, None)
    if not os.path.isdir(path):
        raise TypeError()
    md5_list = []
    for sub_path in os.listdir(path):
        abs_path = os.path.join(path, sub_path)
        if os.path.isdir(abs_path):
            md5_list.append(dir_md5sum(abs_path, cache_map))
        else:
            md5_list.append(file_md5sum(abs_path, cache_map))
    md5_list = sorted(md5_list)
    result = str_md5sum("|".join(md5_list), cache_map)
    cache_map[path] = result
    # print(len(cache_map), path, result)
    return result


def group_by_md5(path_md5_map):
    md5_paths_map = {}
    for path, md5 in path_md5_map.items():
        if md5_paths_map.get(md5, None) is None:
            md5_paths_map[md5] = []
        md5_paths_map[md5].append(path)
    for md5 in md5_paths_map.keys():
        md5_paths_map[md5] = sorted(md5_paths_map[md5])
    return md5_paths_map


def load_all_files(path):
    start_time = time.time()
    file_md5_map = {}
    md5_file_map = {}
    cnt = 0
    size_sum = 0
    last_size = 0
    for root, dirs, files in os.walk(path):
        for file_name in files:
            abs_path = os.path.join(root, file_name)
            size_sum += os.path.getsize(abs_path)
            try:
                md5sum = file_md5sum(abs_path, {})
                file_md5_map[abs_path] = md5sum
                if md5_file_map.get(md5sum, None) is not None:
                    print("%s is dup with %s" % (abs_path, md5_file_map[md5sum]))
                md5_file_map[md5sum] = abs_path
                cnt += 1
                if size_sum - last_size > 1024 * 1024 * 1024:
                    print(
                        "%s:%d files has been scanned,%d dup, %.2fG, %.2fMB/s, file_name=%s" % (datetime.datetime.now(),
                                                                                                cnt,
                                                                                                len(file_md5_map) - len(
                                                                                                    md5_file_map),
                                                                                                size_sum / 1024 / 1024 / 1024,
                                                                                                size_sum / 1024 / 1024 / (
                                                                                                        time.time() - start_time),
                                                                                                file_name))
                    last_size = size_sum
            except PermissionError as e:
                print(e)
    return file_md5_map, md5_file_map


def got_index(file_map):
    md5_map = {}
    for abs_path, md5 in file_map.items():
        if md5_map.get(md5, None) is not None:
            print("%s is dup with %s" % (abs_path, md5_map[md5]))
        md5_map[md5] = abs_path
    print("%d files, got %d md5" % (len(file_map), len(md5_map)))
    return md5_map


def write2csv(path_md5_map, file_name):
    md5_paths_map = group_by_md5(path_md5_map)
    with open(file_name, "w", encoding="utf-8") as f:
        for md5, paths in md5_paths_map.items():
            f.write("%s,%s\n" % (md5, ",".join(paths)))


def scan_path_to_csv(path):
    cache = {}
    dir_md5_map = {}
    file_md5_map = {}
    i = 0
    for root, dirs, files in os.walk(path):
        for file_name in files:
            abs_path = os.path.join(root, file_name)
            md5sum = file_md5sum(abs_path, cache)
            i += 1
            print(i, abs_path, md5sum)
            file_md5_map[abs_path] = md5sum
        for dir_name in dirs:
            abs_path = os.path.join(root, dir_name)
            md5sum = dir_md5sum(abs_path, cache)
            i += 1
            print(i, abs_path, md5sum)
            dir_md5_map[abs_path] = md5sum
    write2csv(dir_md5_map, "dirs.csv")
    write2csv(file_md5_map, "files.csv")


def remove_dup(path):
    start_time = time.time()
    # path = "E:\\test"
    cache = {}
    cnt = 0
    path_list = []
    for root, dirs, files in os.walk(path):
        for file_name in files:
            abs_path = os.path.join(root, file_name)
            path_list.append(abs_path)
            cnt += 1
            print("%d files has been scanned" % cnt)
    path_list = sorted(path_list)
    md5_map = {}
    f = open("dup.txt", "a+", encoding="utf8")
    size_sum = 0
    cnt = 0
    for abs_path in path_list:

        try:
            md5sum = file_md5sum(abs_path, cache)
            new_size = os.path.getsize(abs_path)
            size_sum += new_size
            cnt += 1
            if md5_map.get(md5sum, None) is not None and abs_path != md5_map[md5sum]:
                print("%s is dup with %s" % (abs_path, md5_map[md5sum]))
                f.write("%s is dup with %s\n" % (abs_path, md5_map[md5sum]))
                if new_size == os.path.getsize(md5_map[md5sum]):
                    if len(abs_path) >= len(md5_map[md5sum]) and abs_path.find(
                            "E:\\OneDrive - alumni.hust.edu.cn\\图片") < 0:
                        os.remove(abs_path)
                    elif md5_map[md5sum].find("E:\\OneDrive - alumni.hust.edu.cn\\图片") < 0:
                        os.remove(md5_map[md5sum])
                        md5_map[md5sum] = abs_path
            else:
                md5_map[md5sum] = abs_path
            print("%d: %.2fG has been done,sleep=%.2fMB/s" % (cnt, size_sum / 1024 / 1024 / 1024,
                                                              size_sum / 1024 / 1024 / (time.time() - start_time)))
        except Exception as e:
            pass
    f.close()


def remove_dup_2(base_path, new_paths):
    _, md5_map = load_all_files(base_path)
    for new_path in new_paths:
        new_file_map, _ = load_all_files(new_path)
        for new_file, md5 in new_file_map.items():
            if md5_map.get(md5, None) is not None:
                try:
                    print("%s is dup with %s" % (new_file, md5_map[md5]))
                    os.remove(new_file)
                except PermissionError as e:
                    print(2)


def remove_empty_dir(path):
    my_list = os.listdir(path)
    for sub_path in my_list:
        abs_path = os.path.join(path, sub_path)
        if os.path.isdir(abs_path):
            remove_empty_dir(abs_path)
    my_list = os.listdir(path)
    if len(my_list) <= 0:
        print("%s is empty" % path)
        os.rmdir(path)


if __name__ == '__main__':
    remove_dup_2(base_path="E:\OneDrive - alumni.hust.edu.cn", new_paths=["F:\视频", "F:\百度云盘3", "F:\移动硬盘"])
