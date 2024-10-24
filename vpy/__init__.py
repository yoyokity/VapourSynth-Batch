import os
import shutil
import subprocess
from configparser import ConfigParser


class Vpy:
    source_file = "vpy文件.py"
    destination_file = r"temp\temp.vpy"
    old_string = '$FILE_PATH$'

    def __init__(self, path: str):
        self.path = path

        self._copy()
        self._replace_string()

    def _copy(self):
        shutil.copy2(Vpy.source_file, Vpy.destination_file)

    def _replace_string(self):
        # 读取文件内容
        with open(Vpy.destination_file, 'r', encoding='utf-8') as file:
            content = file.read()

        # 替换字符串
        new_content = content.replace(Vpy.old_string, self.path)

        # 将新内容写回文件
        with open(Vpy.destination_file, 'w', encoding='utf-8') as file:
            file.write(new_content)

    def run(self, config: ConfigParser):
        vsPipe_path = config.get('vapoursynth', 'vsPipe_path')
        output = config.get('video', 'output_path')
        output_format = config.get('video', 'output_format')
        quality = config.get('video', 'quality')
        aq = config.get('video', 'aq')

        input_path, input_filename = os.path.split(self.path)
        input_filename_short = os.path.splitext(input_filename)[0]

        if output == '':
            output_file = os.path.join(input_path, f'[encoded]{input_filename_short}.{output_format}')
        else:
            output_file = os.path.join(output, f'[encoded]{input_filename_short}.{output_format}')

        cmd = [
            f'{vsPipe_path}', '--y4m', f'{Vpy.destination_file}', '-', '|',
            r'tools/nvencc/NVEncC64.exe', '--y4m', '-i', '-', '-c', 'hevc', '--qvbr', f'{quality}',
            '--preset', 'p7', '--lookahead', '12', '--output-depth', '10', '--profile', 'main10',
        ]

        if aq != '':
            cmd.extend(['--aq', '--aq-strength', f'{aq}'])

        cmd.extend(['-o', f'{output_file}'])

        subprocess.run(cmd, shell=True)

        # 删除临时文件
        os.remove(Vpy.destination_file)
