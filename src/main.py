import configparser
import os
import sys
from pathlib import Path

from vpy import Vpy

VIDEO_EXTENSIONS = {
    '.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.m4v', '.ts', '.m2ts', '.mpg', '.mpeg', '.webm'
}


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

    # 筛选视频文件
    input_files = [i for i in input_files if Path(i).suffix.lower() in VIDEO_EXTENSIONS]
    if not input_files:
        print('错误：未检测到任何视频文件！')
        input('按 Enter 退出...')
        exit()

    # 读取配置文件
    config = read_ini('./配置参数.ini')

    # 检查 exe 路径是否正确
    vsPipe_path = config.get('vapoursynth', 'vsPipe_path')
    if not os.path.exists(vsPipe_path):
        print(f'VapourSynth 路径错误！请修改配置文件！')
        input('按 Enter 退出...')
        exit()

    # 获取 vpy 文件路径
    vpy_file = config.get('vapoursynth', 'vpy_file')
    if not vpy_file:
        vpy_file = 'vpy文件.py'

    # 检查 vpy 文件是否存在
    if not os.path.exists(vpy_file):
        print(f'找不到 vpy 文件！')
        input('按 Enter 退出...')
        exit()
    if not vpy_file.endswith('.py'):
        print(f'当前 vpy 文件格式有误，请修改文件后缀为 .py！')
        input('按 Enter 退出...')
        exit()
    with open(vpy_file, 'r', encoding='utf-8') as file:
        content = file.read()
    if not content.find(Vpy.old_string):
        print(f'当前 vpy 文件没有替换字符串 “{Vpy.old_string}”，请修改文件内容！')
        input('按 Enter 退出...')
        exit()

    for input_file in input_files:
        print(f'开始编码：{input_file}')
        vpy = Vpy(input_file, vpy_file)
        vpy.run(config)

    input('编码完成，按 Enter 退出...')
