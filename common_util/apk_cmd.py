# -*- coding: utf-8 -*-
from typing import Union

from common_util.common import Terminal



class ApkCMD(object):
    
    @classmethod
    def depackage(cls, apktool_path:str, apk_path:str, output_dir:str, is_pass_dex:bool, is_only_res:bool)->bool:
        """
        反编 .apk

        :param apktool_path: apktool 路径
        :param apk_path: .apk 路径
        :param output_dir: 反编后目录
        :param is_pass_dex: 是否忽略错误的 .dex, 默认不忽略
        :param is_only_res: 是否只反编译资源文件, 默认编译所有

        java -jar [ apktool 文件] [-s (可选)] d [--only-main-classes (可选)] [需要反编的 .apk 文件] -o [反编后输出的目录]
        """
        pass_dex = ""
        if is_pass_dex:
            pass_dex = " --only -main-classes"
        
        s = ""
        if is_only_res:
            s = " -s"
        cmd = "java -jar \"{0}\"{1} d{2} \"{3}\" -f -o \"{4}\"".format(
            apktool_path, s, pass_dex, apk_path, output_dir)
        return Terminal.getstatusoutput(cmd)
    
