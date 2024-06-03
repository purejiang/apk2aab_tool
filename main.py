"""APK2AAB Tool V1.

Usage:
  main.py apk2aab SRC OUT CONF
  main.py (-h | --help)
  main.py (-v | -version)

Options and arguments:
  -h --help            显示帮助信息.
  -v --version         显示当前工具版本信息.
  SRC                  指定APK包
  OUT                  最终输出的AAB文件或者目录
  CONF                 打包配置文件
  --workspace=<path>   打包需要的临时的工作空间
  -d --debug           是否debug模式，是的话，最终包以工程压缩包的形式输出
  -k --keeptmp         是否保留临时目录
"""
from docopt import docopt

import constant.param
from command.apk2aab import Apk2AabCommand

if __name__ == '__main__':
    arguments = docopt(__doc__, version='APK2AAB Tool V1')
    if arguments[constant.param.CmdParam.COMMAND.APK2AAB]:
        Apk2AabCommand(arguments).build()