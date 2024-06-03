import datetime
import inspect
import json
import os
import traceback
from abc import ABCMeta, abstractmethod

from common_util import annotation
from common_util.common import Logger


class BaseCommand(metaclass=ABCMeta):

    def __init__(self, cmd_args):
        self.logger = Logger()
        self.cmd_args = cmd_args
        self.param_dic = {}

    @abstractmethod
    def _config_params(self, param_dic):
        pass

    @abstractmethod
    def _config_workspace(self, param_dic):
        pass

    def build(self):
        try:
            start_time = datetime.datetime.now()
            is_succ = self._config_params(self.param_dic)
            if is_succ:
                is_succ = self._config_workspace(self.param_dic)
            if is_succ:
                is_succ = self._on_build(self.param_dic)
        except Exception as ex:
            msg = traceback.format_exc()
            self.logger.error(msg)
        finally:
            self._on_finish(self.param_dic)
        end_time = datetime.datetime.now()
        time_difference = (end_time - start_time).total_seconds()
        self.logger.info("执行完成，总耗时：%s 分 %s 秒" % (int(time_difference / 60), time_difference % 60))
        pass

    @abstractmethod
    def _on_build(self, param_dic):
        pass

    @abstractmethod
    def _on_finish(self, param_dic):
        pass


class MainlineTask(metaclass=ABCMeta):

    def __init__(self, param_dic):
        self.logger = Logger()
        self.param_dic = param_dic

    def execute(self):
        start_time = datetime.datetime.now()
        funcs = inspect.getmembers(self.__class__, inspect.isfunction)
        func_list = []
        for (name, func) in funcs:  # 遍历类中的函数
            if func.__annotations__ and func.__annotations__["name"] == annotation.mainline.__name__:
                func_list.append(func)
        func_list = sorted(func_list, key=lambda x: x.__annotations__["step"])
        self.logger.info("------------------------" + self.__class__.__name__ + "开始------------------------")
        for func in func_list:
            if not func.__annotations__["enable"]:
                self.logger.info("\"%s\" 已被禁用，不需要执行。" % func.__annotations__["desc"])
                continue
            if not func(self, self.param_dic):
                self.logger.info("\"%s\" 执行失败，退出任务 %s。" % (func.__annotations__["desc"], self.__class__.__name__))
                return False
        end_time = datetime.datetime.now()
        time_difference = (end_time - start_time).total_seconds()
        self.logger.info("------------------------ %s 结束 - 耗时：%s 秒------------------------" % (self.__class__.__name__, time_difference))
        return True