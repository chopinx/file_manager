import hashlib
import os


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
    with open(path, 'rb') as f:
        for line in f:
            m.update(line)
    result = m.hexdigest()
    cache_map[path] = result
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


def write2csv(path_md5_map, file_name):
    md5_paths_map = group_by_md5(path_md5_map)
    with open(file_name, "w") as f:
        for md5, paths in md5_paths_map.items():
            f.write("%s,%s\n" % (md5, ",".join(paths)))


if __name__ == '__main__':
    path = "/Users/chopin/OneDrive"
    cache = {}
    dir_md5_map = {}
    file_md5_map = {}
    for root, dirs, files in os.walk(path):
        for dir_name in dirs:
            abs_path = os.path.join(root, dir_name)
            md5sum = dir_md5sum(abs_path, cache)
            print(abs_path, md5sum)
            dir_md5_map[abs_path] = md5sum
        for file_name in files:
            abs_path = os.path.join(root, file_name)
            md5sum = file_md5sum(abs_path, cache)
            print(abs_path, md5sum)
            file_md5_map[abs_path] = md5sum
    write2csv(dir_md5_map, "dirs.csv")
    write2csv(file_md5_map, "files.csv")
