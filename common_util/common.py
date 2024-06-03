# encoding: utf-8

"""
@author: SoGood
@time: 2018/5/16 下午8:31

@desc:

"""
import subprocess
import os
import sys
import time
import logging
import zipfile


def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


@Singleton
class Logger:
    def __init__(self, set_level="INFO",
                 name=os.path.split(os.path.splitext(sys.argv[0])[0])[-1],
                 log_name=time.strftime("%Y-%m-%d.log", time.localtime()),
                 log_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "log"),
                 use_console=True, save_file=False):
        """
        :param set_level: 日志级别["NOTSET"|"DEBUG"|"INFO"|"WARNING"|"ERROR"|"CRITICAL"]，默认为INFO
        :param name: 日志中打印的name，默认为运行程序的name
        :param log_name: 日志文件的名字，默认为当前时间（年-月-日.log）
        :param log_path: 日志文件夹的路径，默认为logger.py同级目录中的log文件夹
        :param use_console: 是否在控制台打印，默认为True
        """
        if not set_level:
            set_level = self._exec_type()  # 设置set_level为None，自动获取当前运行模式
        self.__logger = logging.getLogger(name)
        self.setLevel(
            getattr(logging, set_level.upper()) if hasattr(logging, set_level.upper()) else logging.INFO)  # 设置日志级别
        if not os.path.exists(log_path) and save_file:  # 创建日志目录
            os.makedirs(log_path)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        handler_list = list()
        if save_file:
            handler_list.append(logging.FileHandler(os.path.join(log_path, log_name), encoding="utf-8"))
        if use_console:
            handler_list.append(logging.StreamHandler())
        for handler in handler_list:
            handler.setFormatter(formatter)
            self.addHandler(handler)

    def __getattr__(self, item):
        return getattr(self.logger, item)

    @property
    def logger(self):
        return self.__logger

    @logger.setter
    def logger(self, func):
        self.__logger = func

    def _exec_type(self):
        return "DEBUG" if os.environ.get("IPYTHONENABLE") else "INFO"

    # logger.critical("这是一个 critical 级别的问题！")
    # logger.error("这是一个 error 级别的问题！")
    # logger.warning("这是一个 warning 级别的问题！")
    # logger.info("这是一个 info 级别的问题！")
    # logger.debug("这是一个 debug 级别的问题！")


class Terminal:

    @classmethod
    def exe(cls, cmd):
        logger = Logger()
        logger.info("执行命令：" + cmd)
        rsl = subprocess.getstatusoutput(cmd)
        if rsl[0] != 0:
            raise OSError(rsl[0], rsl[1])

        if rsl[1]:
            return rsl[1]

    @classmethod
    def exe_with_return(cls, cmd):
        logger = Logger()
        logger.info("执行命令 exe_with_return：" + cmd)
        rsl = subprocess.getstatusoutput(cmd)
        return rsl[0], rsl[1]

    @classmethod
    def getstatusoutput(cls, cmd):
        logger = Logger()
        logger.info("执行命令 getstatusoutput：" + cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, bufsize=1)
        out = ""
        for line in iter(process.stdout.readline, b''):
            out += line.decode("cp437")
        process.stdout.close()
        process.wait()
        # print(process.returncode)
        # print(out)
        logger.info(out)
        # if process.returncode != 0:
        if process.returncode == 0:
            return True
        else:
            return False


def compared_version(ver1, ver2):
    """
    传入不带英文的版本号,特殊情况："10.12.2.6.5">"10.12.2.6"
    :param ver1: 版本号1
    :param ver2: 版本号2
    :return: ver1< = >ver2返回-1/0/1
    """
    list1 = str(ver1).split(".")
    list2 = str(ver2).split(".")
    # print(list1)
    # print(list2)
    # 循环次数为短的列表的len
    for i in range(len(list1)) if len(list1) < len(list2) else range(len(list2)):
        if int(list1[i]) == int(list2[i]):
            pass
        elif int(list1[i]) < int(list2[i]):
            return -1
        else:
            return 1
    # 循环结束，哪个列表长哪个版本号高
    if len(list1) == len(list2):
        return 0
    elif len(list1) < len(list2):
        return -1
    else:
        return 1


def is_empty(key, param_dic):
    """
    判断key在字典param_dic中是否存在，其值是否为空
    :param key:
    :param param_dic:
    :return:
    """
    if key not in param_dic:
        return True
    if str(param_dic[key]).strip() == "":
        return True
    return False


def is_not_empty(key, param_dic):
    """
    判断key在字典param_dic中是否存在，其值是否非空
    :param key:
    :param param_dic:
    :return:
    """
    if key not in param_dic:
        return False
    if str(param_dic[key]).strip() == "" or str(param_dic[key]).strip() == "None":
        return False
    return True


def zip_dir(dir_path, out_zip_name):
    """
    压缩指定文件夹
    :param dir_path: 目标文件夹路径
    :param out_zip_name: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    logger = Logger()
    zip = zipfile.ZipFile(out_zip_name, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dir_path):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dir_path, '')

        for filename in filenames:
            logger.info("文件%s写入到%s" % (os.path.join(path, filename), os.path.join(fpath, filename)))
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.close()


if __name__ == '__main__':
    # zipFile = zipfile.ZipFile("../tmp/out.zip", "w", zipfile.ZIP_DEFLATED)
    zip_dir("../tmp/tmp_20221026_200108/app", "../tmp/out.zip")
