import json
import os
import re

from pyjavaproperties import Properties

from common_util.common import Logger, compared_version
from constant.param import PackParam


def get_properties(properties_filepath):
    """
    从properties 文件中获取参数
    :param properties_filepath: properties 文件路径
    :return: 返回字典
    """
    properties = Properties()
    properties.load(open(properties_filepath, 'r', encoding='utf-8'))
    return properties.getPropertyDict()


def get_json(json_filepath, encoding="utf-8"):
    """
    文件中保存的数据为json格式，获取其内容（用于适配旧版打包工具，旧版打包工具参数文件为json格式）
    :param json_filepath: 文件路径
    :param encoding:
    :return:
    """
    with open(json_filepath, 'r', encoding=encoding) as fp:
        json_data = json.load(fp)
        return json_data


def get_params_from_jsonconfig(json_data):
    """
    从打包json配置文件中处理出参数集
    :return:
    """
    logger = Logger()
    param_dic = {}
    if "config" in json_data:
        param_dic.update(json_data["config"])
    if "lib" in json_data:
        # 将 {"lib": {"aa": "google", "bb": "facebook"} 的参数转换为lib.aa, lib.bb 的形式保存
        for (k, v) in json_data["lib"].items():
            param_dic["lib." + k] = v
    if "placeholder" in json_data:
        param_dic[PackParam.PLACEHOLDER] = json_data["placeholder"]  # 读取channel_config中placeholder参数
    logger.info("测试输出-" + str(param_dic))
    return param_dic


def replace_dic_placeholders(param_dic, field=None):
    """
    替换字典中的占位符变量
    :param param_dic: 需要替换的字典&用来替换的变量的参数的字典
    :param field: 指定替换某个字段值，为空则整个字典中的变量都进行替换
    :return:
    """
    logger = Logger()
    to_remove_keys = []
    for (k, v) in param_dic.items():
        refre = re.compile('{[^\"]+?}')     # 占位符是 '{}'
        if not isinstance(v, str):
            continue
        refs = refre.findall(v)     # 查找所有带有占位符的字典值
        for ref in refs:
            to_replace_key = ref[1:-1]
            if field:
                if field == to_replace_key:
                    # param_dic[k] = v.replace(ref, param_dic[to_replace_key])  # error
                    param_dic[k] = param_dic[k].replace(ref, param_dic[to_replace_key])
                    logger.info("设置%s中的%s变量，结果：%s" % (k, to_replace_key, param_dic[k]))
            else:
                #print(ref)  {gradle_version}
                if to_replace_key in param_dic and param_dic[to_replace_key]:  # 字典中已存在的变量可以匹配到了占位符，并且不为空
                    # param_dic[k] = v.replace(ref, param_dic[to_replace_key])  # error
                    param_dic[k] = param_dic[k].replace(ref, param_dic[to_replace_key])
                    logger.info("设置%s中的%s变量，结果：%s" % (k, to_replace_key, param_dic[k]))
                else:                       # 字典中匹配不到带有变量符的变量，直接删除该参数
                    logger.info("在字典中找不到参数 %s 去替换变量 %s 的值" % (to_replace_key, k))
                    if k not in to_remove_keys:
                        to_remove_keys.append(k)
    for key in to_remove_keys:
        logger.info("从参数集中删除参数%s: %s" % (key, param_dic[key]))
        del param_dic[key]


def replace_properites_placeholders(properties_file, param_dic):
    """
    替换properties 文件中的变量
    :param properties_file: 需要使用参数集替换变量的文件
    :param param_dic: 包含key-value的字典，与properties_file里的变量相同key时，使用字典中的值将其替换
    :return:
    """
    logger = Logger()
    logger.info("替换文件%s中的变量。" % properties_file)
    placeholder_pro = Properties()
    pf = open(properties_file)
    placeholder_pro.load(pf)
    pf.close()
    p_dic = placeholder_pro.getPropertyDict()
    out_placeholder_pro = Properties()
    pfo = open(properties_file, "w")
    for key in p_dic.keys():
        if key in param_dic:
            logger.info("设置参数 %s=%s" % (key, param_dic[key]))
            out_placeholder_pro.setProperty(key, str(param_dic[key]))
        else:
            out_placeholder_pro.setProperty(key, p_dic[key])
            logger.info("使用参数默认值 %s=%s" % (key, p_dic[key]))
    out_placeholder_pro.store(pfo)


def add_or_update_params_pros(properties_file, param_dic):
    """
    在properties 文件中添加变量，已存在则不进行修改
    :param properties_file:
    :param param_dic:
    :return:
    """
    logger = Logger()
    pros = Properties()
    if os.path.exists(properties_file):
        pf = open(properties_file)
        pros.load(pf)
        pf.close()
    ori_dic = pros.getPropertyDict()
    pfo = open(properties_file, "w")
    out_placeholder_pro = Properties()
    for (key, value) in ori_dic.items():
        out_placeholder_pro.setProperty(key, value)
    for (key, value) in param_dic.items():
        logger.info("添加参数%s=%s 到 %s" % (key, value, properties_file))
        out_placeholder_pro.setProperty(key, value)
    out_placeholder_pro.store(pfo)


def replace_file_placeholders(file, param_dic):
    """
    替换文件中的变量。变量形式如： '${var}'
    :param file:
    :param param_dic:
    :return:
    """
    # TODO 需要分开判断是否manifest.xml , .gradle。然后不获取替换注释
    file_content = ""
    logger = Logger()
    logger.info("替换文件%s中的变量占位符。" % file)
    with open(file, 'r', encoding="utf-8") as f:
        for line in f:
            file_content += line
    f.close()
    refre = re.compile('\${.+?}')  # 占位符是 '{}' 或者 '${}'
    refs = refre.findall(file_content)  # 查找所有带有占位符的字典值
    for ref in refs:
        key = ref[2: -1]
        if key in param_dic:
            to_rep_value = param_dic[key]
            if isinstance(to_rep_value, bool):
                to_rep_value = str(to_rep_value).lower()
            file_content = file_content.replace(ref, to_rep_value)
            logger.info("替换%s为%s" % (ref, to_rep_value))
        else:
            logger.error("找不到参数%s, 替换${%s}失败。" % (key, key))
    f = open(file, 'wb+')
    f.write(file_content.encode('utf-8'))


def get_version_str(dirpath):
    """
    从目录中遍历文件夹，将文件夹名转为版本号，从中获取最大的版本号。
    :param dirpath: 目录路径
    :return: 版本号
    """
    current_max_version = 0
    default_dirname = ""
    for dirname in os.listdir(dirpath):
        # 从文件夹名取出版本号进行对比，获取数值最大的
        remove_chars = '[a-zA-Z]+'  # 删除目录中的英文字符
        ver_str = re.sub(remove_chars, '', dirname)
        remove_chs = '[\u4e00-\u9fa5]+'     # 删除中文
        ver_str = re.sub(remove_chs, '', ver_str)
        ver_str = ver_str.replace("_", "0").replace("-", "0")   # 将目录中的 "_", "-" 替换为0
        if ver_str.endswith("."):   # 版本号以 . 结尾的 ，删除该字符 "."
            ver_str = ver_str[:-1]
        if ver_str.startswith("."):
            ver_str = ver_str[1:]
        if not ver_str:
            continue
        # Logger().info("dirname: %s, ver_str：%s，current_version：%s" % (dirname, ver_str, current_max_version))
        if compared_version(ver_str, current_max_version) == 1:
            current_max_version = ver_str
            default_dirname = dirname
    # Logger().info(default_dirname)
    return default_dirname
