import inspect

from common_util.common import Logger

"""
def operation(**kwds):
    def decorate(fn):
        for item in kwds.items():
            # print(item)
            fn.__annotations__[item[0]] = item[1]
        print("operation wrapper")
        return fn
    return decorate

def operation(priority, desc):
    def decorate(fn):
        fn.__annotations__["priority"] = priority
        fn.__annotations__["desc"] = desc
        print("operation wrapper")
        return fn
    return decorate
"""


def mainline(step, desc, enable=True):
    def decorate(fn):
        def func(*args, **kwargs):
            logger = Logger()
            logger.info("-- %s.%s --" % (str(step), desc))
            from command.base import MainlineTask
            if not isinstance(args[0], MainlineTask) or not isinstance(args[1], dict):
                logger.info("函数 \"%s.%s\" %s 所在类的类型不对或函数参数不对。" % (args[0].__class__.__name__, fn.__name__, desc))
                return False
            is_success = fn(*args, **kwargs)
            if not isinstance(is_success, bool):
                logger.info("函数 \"%s.%s\" %s 返回值不对。" % (args[0].__class__.__name__, fn.__name__, desc))
                return False
            return is_success
        func.__annotations__["step"] = step
        func.__annotations__["desc"] = desc
        func.__annotations__["enable"] = enable
        func.__annotations__["name"] = mainline.__name__
        return func
    return decorate


def operation(timing, priority, desc, enable=True, extra_cmd=None):
    def decorate(fn):
        def func(*args, **kwargs):
            logger = Logger()
            logger.info("---- %s).%s --" % (str(priority), desc))
            if not isinstance(args[1], dict):
                logger.info("函数 \"%s.%s\" %s 函数参数不对。" % (args[0].__class__.__name__, fn.__name__, desc))
                return False
            is_success = fn(*args, **kwargs)
            if not isinstance(is_success, bool):
                logger.info("函数 \"%s.%s\" %s 返回值不对。" % (args[0].__class__.__name__, fn.__name__, desc))
                return False
            return is_success
        func.__annotations__["timing"] = timing
        func.__annotations__["priority"] = priority
        func.__annotations__["desc"] = desc
        func.__annotations__["enable"] = enable
        func.__annotations__["extra_cmd"] = extra_cmd
        func.__annotations__["name"] = operation.__name__
        return func
    return decorate


# class TestClass(MainlineTask):
#
#     @mainline(step=1, desc="描述描述描述")
#     def test_func(self, param_dic):
#         print("test_func ， param = " + str(param_dic))
#         return True
#
#
# if __name__ == '__main__':
#     testClass = TestClass()
#     funcs = inspect.getmembers(TestClass, inspect.isfunction)
#     for (name, func) in funcs:  # 遍历模块中的类
#         if func.__annotations__ and func.__annotations__["name"] == mainline.__name__:
#             func(testClass, {"param": "param1", "param2": "param2"})
#             # func(testClass, "asdf")

# 参考资料：https://www.runoob.com/w3cnote/python-func-decorators.html
""" annotation 含义
def spamrun(fn):
    def sayspam(*args):
        print("spam,spam,spam")
        fn(*args)

    return sayspam

def useful(a, b):
    print(a * b)

if __name__ == "__main__"
    useful = spamrun(useful)
    useful(a, b)
    
"""
