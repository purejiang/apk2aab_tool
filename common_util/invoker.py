import importlib
import inspect
import os
from abc import ABCMeta, abstractmethod

from common_util import annotation
from common_util.common import Logger
from constant.param import Apk2AabEnvirParam

def _load_clazz_function(moudle, clazz_name, param_dic):
    clsmembers = inspect.getmembers(moudle, inspect.isclass)
    object_func_dic = {}
    for (name, clazz) in clsmembers:  # 遍历模块中的类
        for base in clazz.__bases__:  # 遍历类的父类
            if base.__name__ == clazz_name:
                # print("----%s-----" % str(clazz()))
                funcs = inspect.getmembers(clazz, inspect.isfunction)
                func_list = []
                for (name, func) in funcs:  # 遍历类中的函数
                    if func.__annotations__ and func.__annotations__["name"] == annotation.operation.__name__:
                        func_list.append(func)
                func_list = sorted(func_list, key=lambda x: x.__annotations__["priority"])
                # print(func_list)
                object_func_dic[clazz(param_dic)] = func_list
    return object_func_dic


def _load_clazz_obj(moudle_path, clazz_name, param_dic):
    logger = Logger()
    object_list = []
    if os.path.exists(moudle_path):
    # if os.path.exists(os.path.join("..", moudle_path)):
        module = importlib.import_module(moudle_path.replace("/", ".").replace(".py", ""))
        clsmembers = inspect.getmembers(module, inspect.isclass)
        for (name, clazz) in clsmembers:  # 遍历模块中的类
            for base in clazz.__bases__:  # 遍历类的父类
                if base.__name__ == clazz_name:
                    object_list.append(clazz(param_dic))
    else:
        logger.info("模块%s不存在。跳过" % moudle_path)
    return object_list


class Apk2AabSpecialHandler(object):

    def __init__(self, param_dic):
        self.param_dic = param_dic
        self.smali_game_scripts_list = []
        self.smali_channel_scripts_list = []
        self.smali_game_channel_scripts_list = []
        self.gradle_game_scripts_list = []
        self.gradle_channel_scripts_list = []
        self.gradle_game_channel_scripts_list = []
        self.game_skin_scripts_list = []
        self.extra_script_inited = False
        self.logger = Logger()

    def _init_extra_scripts(self):
        if not self.extra_script_inited:
            self.game_scripts_list = _load_clazz_obj(self.param_dic[Apk2AabEnvirParam.GAME_EXTRA_SCRIPTS],
                                                           Apk2AabExtraHandler.__name__, self.param_dic)
            self.channel_scripts_list = _load_clazz_obj(self.param_dic[Apk2AabEnvirParam.CHANNEL_EXTRA_SCRIPTS],
                                                              Apk2AabExtraHandler.__name__, self.param_dic)
            self.game_channel_scripts_list = _load_clazz_obj(self.param_dic[Apk2AabEnvirParam.GAME_CHANNEL_EXTRA_SCRIPTS],
                                                                   Apk2AabExtraHandler.__name__, self.param_dic)
            self.extra_script_inited = True
    
    def handle_before_merge_params(self)->bool:
        """
        参数处理前的逻辑
        :return:
        """
        self._init_extra_scripts()
        result = True
        for game_script in self.game_scripts_list:
            result = result and game_script.before_merge_params()
        for channel_script in self.channel_scripts_list:
            result = result and channel_script.before_merge_params()
        for game_channel_script in self.game_channel_scripts_list:
            result = result and game_channel_script.before_merge_params()
        return result

    def handle_before_depackage(self)->bool:
        """
        反编译apk前的逻辑
        :return:
        """
        self._init_extra_scripts()
        result = True
        for game_script in self.game_scripts_list:
            result = result and game_script.before_depackage()
        for channel_script in self.channel_scripts_list:
            result = result and channel_script.before_depackage()
        for game_channel_script in self.game_channel_scripts_list:
            result = result and game_channel_script.before_depackage()
        return result

    def handle_before_compile_res(self)->bool:
        """
        编译 base 资源前
        :return:
        """
        self._init_extra_scripts()
        result = True
        for game_script in self.game_scripts_list:
            result = result and game_script.before_compile_res()
        for channel_script in self.channel_scripts_list:
            result = result and channel_script.before_compile_res()
        for game_channel_script in self.game_channel_scripts_list:
            result = result and game_channel_script.before_compile_res()
        return result
    
    def handle_before_link_res(self)->bool:
        """
        链接base资源前的逻辑
        :return:
        """
        self._init_extra_scripts()
        result = True
        for game_script in self.game_scripts_list:
            result = result and game_script.before_link_res()
        for channel_script in self.channel_scripts_list:
            result = result and channel_script.before_link_res()
        for game_channel_script in self.game_channel_scripts_list:
            result = result and game_channel_script.before_link_res()
        return result
    
    def handle_before_arrange_base(self)->bool:
        """
        整理 base 模块前的逻辑
        :return:
        """
        self._init_extra_scripts()
        result = True
        for game_script in self.game_scripts_list:
            result = result and game_script.before_arrange_base()
        for channel_script in self.channel_scripts_list:
            result = result and channel_script.before_arrange_base()
        for game_channel_script in self.game_channel_scripts_list:
            result = result and game_channel_script.before_arrange_base()
        return result
    
    def handle_before_arrange_assets(self)->bool:
        """
        整理 gameassets 模块前的逻辑
        :return:
        """
        self._init_extra_scripts()
        result = True
        for game_script in self.game_scripts_list:
            result = result and game_script.before_arrange_assets()
        for channel_script in self.channel_scripts_list:
            result = result and channel_script.before_arrange_assets()
        for game_channel_script in self.game_channel_scripts_list:
            result = result and game_channel_script.before_arrange_assets()
        return result
    

    def handle_before_link_assets(self)->bool:
        """
        链接 gameassets 模块资源前的逻辑
        :return:
        """
        self._init_extra_scripts()
        result = True
        for game_script in self.game_scripts_list:
            result = result and game_script.before_link_assets()
        for channel_script in self.channel_scripts_list:
            result = result and channel_script.before_link_assets()
        for game_channel_script in self.game_channel_scripts_list:
            result = result and game_channel_script.before_link_assets()
        return result
    
    def handle_before_bundle_build(self)->bool:
        """
        构建 aab 前的逻辑
        :return:
        """
        self._init_extra_scripts()
        result = True
        for game_script in self.game_scripts_list:
            result = result and game_script.before_bundle_build()
        for channel_script in self.channel_scripts_list:
            result = result and channel_script.before_bundle_build()
        for game_channel_script in self.game_channel_scripts_list:
            result = result and game_channel_script.before_bundle_build()
        return result
    
    def handle_before_signer_aab(self)->bool:
        """
        签名前的逻辑
        :return:
        """
        self._init_extra_scripts()
        result = True
        for game_script in self.game_scripts_list:
            result = result and game_script.before_signer_aab()
        for channel_script in self.channel_scripts_list:
            result = result and channel_script.before_signer_aab()
        for game_channel_script in self.game_channel_scripts_list:
            result = result and game_channel_script.before_signer_aab()
        return result


class Apk2AabExtraHandler(metaclass=ABCMeta):

    def __init__(self, param_dic):
        self.logger = Logger()
        self.param_dic = param_dic
    
    @abstractmethod
    def before_merge_params(self):
        return True

    @abstractmethod
    def before_depackage(self):
        return True
        
    @abstractmethod
    def before_compile_res(self):
        return True
    
    @abstractmethod
    def before_link_res(self):
        return True 
    
    @abstractmethod
    def before_arrange_base(self):
        return True  
    
    @abstractmethod
    def before_arrange_assets(self):
        return True  
        
    @abstractmethod
    def before_link_assets(self):
        return True

    @abstractmethod
    def before_bundle_build(self):
        return True  

    @abstractmethod
    def before_signer_aab(self):
        return True  




