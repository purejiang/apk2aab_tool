# -*- coding: utf-8 -*-

import os

class FileUtils:
    @classmethod
    def replaceFileNames(cls, parent_dir):
        for root, dirs, files in os.walk(parent_dir):
            for file in files:
                # 遍历drawable中所有$开头的文件
                full_path = os.path.join(root, file)
                
                file_name = os.path.basename(file)
                if file_name.startswith("$"):
                    new_full_path = os.path.join(root, file_name.replace("$", ""))
                    os.rename(full_path, new_full_path)
    @classmethod                
    def replaceFielContent(cls, file_path, kvs):
        with open(file_path, "r+", encoding="utf-8") as file:
            content = file.read()
            for key in kvs:
                content = content.replace(str(key), str(kvs[key]))
            file.seek(0)
            file.truncate()
            file.write(content)