import os
import sys
import configparser

from vpy import Vpy


def read_ini(path) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(path, encoding='utf-8')
    return config


# 设置工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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
    config = read_ini('配置参数.ini')

    #检查exe路径是否正确
    vsPipe_path = config.get('vapoursynth', 'vsPipe_path')
    if not os.path.exists(vsPipe_path):
        print(f"VapourSynth路径错误！请修改配置文件！")
        input("按 Enter 退出...")
        exit()

    #
    for input_file in input_files:
        print(f"开始编码 {input_file}")
        vpy = Vpy(input_file)
        vpy.run(config)

    input("编码完成，按 Enter 退出...")
