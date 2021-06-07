try:
    import os
    import sys
    import difflib
    import hashlib
except Exception as e:
    print('Error:', e)
    os.system("pause")
    sys.exit()


IGNORE_FILES_EXTS = 'jpg', 'jpeg', 'png', 'ttf', 'mo', 'so', 'bin', 'cgi', 'ico'
DELIMITER = '-' * 75


def compare_files(path_to_file1, path_to_file2, mode="r", encoder=None):
    if encoder:
        file1 = open(path_to_file1, mode, encoding=encoder)
        file2 = open(path_to_file2, mode, encoding=encoder)
    else:
        file1 = open(path_to_file1, mode)
        file2 = open(path_to_file2, mode)

    if mode == "r":
        diff = difflib.unified_diff(
            file1.readlines(),
            file2.readlines(),
            fromfile=path_to_file1,
            tofile=path_to_file2)
    elif mode == "rb":
        hash1 = hashlib.md5()
        hash2 = hashlib.md5()
        hash1.update(file1.read())
        hash2.update(file2.read())

        diff = difflib.unified_diff(
            ['md5: {}'.format(hash1.hexdigest())],
            ['md5: {}'.format(hash2.hexdigest())],
            fromfile=path_to_file1,
            tofile=path_to_file2
            )
    else:
        print('Wrong mode selected!')

    delimiter_flag = False
    for line in diff:
        delimiter_flag = True
        print(line)

    if delimiter_flag:
        print(DELIMITER)

    file1.close()
    file2.close()


def bin_walk(path1, path2):
    while path1.endswith(('\\', '/', ' ')):
        path1 = path1[:-1]
    while path2.endswith(('\\', '/', ' ')):
        path2 = path2[:-1]

    for path in (path1, path2):
        if not os.path.exists(path) or not os.path.isdir(path):
            print('Path doesn\'t exist: {}'.format(path))
            return

    for (dirpath_1, dirnames_1, filenames_1) in os.walk(path1):
        filenames_1 = set(filenames_1)
        dirnames_1 = set(dirnames_1)
        filenames_2 = set()
        dirnames_2 = set()

        dirpath_2 = os.path.join(path2, dirpath_1[len(path1)+1:])
        while dirpath_2.endswith(('\\', '/', ' ')):
            dirpath_2 = dirpath_2[:-1]

        if os.path.exists(dirpath_2):
            for entry in os.listdir(dirpath_2):
                if os.path.isfile(os.path.join(dirpath_2, entry)):
                    filenames_2.add(entry)
                elif os.path.isdir(os.path.join(dirpath_2, entry)):
                     dirnames_2.add(entry)
                else:
                    pass

            difference_in_files = filenames_1 ^ filenames_2
            difference_in_folders = dirnames_1 ^ dirnames_2
            filenames = filenames_1 & filenames_2

            if len(difference_in_folders) != 0:
                for i, path in enumerate((dirpath_1, dirpath_2)):
                    for folder in difference_in_folders:
                        if not os.path.isdir((os.path.join(path, folder))):
                            print('Folder doesn\'t exist: {}'.format(os.path.join(path, folder)))
                            for (missing_paths, _, missing_files) in os.walk(os.path.join(dirpath_2 if i == 0 else dirpath_1, folder)):
                                for mis_file in missing_files:
                                    missing_path = os.path.join(dirpath_1 if i == 0 else dirpath_2, missing_paths[len(dirpath_2 if i == 0 else dirpath_1)+1:], mis_file)
                                    print('File doesn\'t exist: {}'.format(missing_path))
                            print(DELIMITER)

            if len(difference_in_files) != 0:
                for path in (dirpath_1, dirpath_2):
                    for file in difference_in_files:
                        if not os.path.isfile((os.path.join(path, file))):
                            print('File doesn\'t exist: {}'.format(os.path.join(path, file)))
                            print(DELIMITER)

            for file in filenames:
                if not file.lower().endswith(IGNORE_FILES_EXTS):
                    filename1 = os.path.join(dirpath_1, file)
                    filename2 = os.path.join(dirpath_2, file)

                    try:
                        compare_files(filename1, filename2, encoder="utf-8")
                    except UnicodeDecodeError as e:
                        try:
                            compare_files(filename1, filename2, encoder="utf16")
                        except UnicodeError as e:
                            try:
                                compare_files(filename1, filename2, mode="rb")
                            except:
                                print('Can\'t open file: {}'.format(filename2))
                                print(DELIMITER)


if __name__ == '__main__':
    path1 = sys.argv[1]
    path2 = sys.argv[2]
    bin_walk(path1, path2)
