import os
import sys
import configparser

from pathlib import Path
from vpy import Vpy


def read_ini(path) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(path, encoding='utf-8')
    return config


# 设置工作目录
os.chdir(Path(__file__).resolve().parent.parent)

if __name__ == '__main__':
    # 获取拖入的文件路径列表
    _input_files = sys.argv[1:]
    _input_files = ' '.join(_input_files)
    _input_files = _input_files.split(' ')

    input_files = []
    for i in _input_files:
        if i[1:3] == ':\\':
            input_files.append(i)
        else:
            input_files[-1] = input_files[-1] + ' ' + i

    # 读取配置文件
    config = read_ini('./配置参数.ini')

    # 检查exe路径是否正确
    vsPipe_path = config.get('vapoursynth', 'vsPipe_path')
    if not os.path.exists(vsPipe_path):
        print(f"VapourSynth路径错误！请修改配置文件！")
        input("按 Enter 退出...")
        exit()

    # 获取vpy文件路径
    vpy_file = config.get('vapoursynth', 'vpy_file')
    if not vpy_file:
        vpy_file = 'vpy文件.py'

    # 检查vpy文件是否存在
    if not os.path.exists(vpy_file):
        print(f"找不到vpy文件！")
        input("按 Enter 退出...")
        exit()
    if not vpy_file.endswith('.py'):
        print(f"当前vpy文件格式有误，请修改文件后缀为.py！")
        input("按 Enter 退出...")
        exit()
    with open(vpy_file, 'r', encoding='utf-8') as file:
        content = file.read()
    if not content.find(Vpy.old_string):
        print(f"当前vpy文件没有替换字符串 “{Vpy.old_string}” ，请修改文件内容！")
        input("按 Enter 退出...")
        exit()

    #
    for input_file in input_files:
        print(f"开始编码 {input_file}")
        vpy = Vpy(input_file, vpy_file)
        vpy.run(config)

    input("编码完成，按 Enter 退出...")
