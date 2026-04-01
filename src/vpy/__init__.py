import os
import shutil
import subprocess
from configparser import ConfigParser
from pathlib import Path

from vpy.extract_chapter import extract_chapter


class Vpy:
    source_file = "vpy文件.py"
    destination_file = r"temp\temp.vpy"
    old_string = '$FILE_PATH$'

    def __init__(self, path: str, vpy_file: str):
        self.path = path
        Vpy.source_file = vpy_file
        self.nvencc_path = Path(os.getcwd()).joinpath(r'tools\nvencc\NVEncC64.exe')
        self.ffmpeg_path = Path(os.getcwd()).joinpath(r'tools\ffmpeg\ffmpeg.exe')
        self.mkvextract_path = Path(os.getcwd()).joinpath(r'tools\mkv\mkvextract.exe')
        self.mkvmerge_path = Path(os.getcwd()).joinpath(r'tools\mkv\mkvmerge.exe')

        self.章节文件缓存 = Path(os.getcwd()).joinpath(r'temp\chapters.xml')

        self._copy()
        self._replace_string()

    @staticmethod
    def _copy():
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

    def _get_parameter(self, config: ConfigParser):
        # vs相关
        self.vs_vsPipe_path = config.get('vapoursynth', 'vsPipe_path')

        # video相关
        self.video_output = config.get('video', 'output_path')
        self.video_output_format = config.get('video', 'output_format')
        self.video_quality = config.get('video', 'quality')
        self.video_aq = config.get('video', 'aq')
        self.video_chapter_copy = config.getboolean('video', 'chapter_copy', fallback=True)
        self.video_key_on_chapter = config.getboolean('video', 'key_on_chapter', fallback=True)

        # audio相关
        self.audio_codec = config.get('audio', 'codec')
        self.audio_bitrate = config.get('audio', 'bitrate')
        self.audio_samplerate = config.get('audio', 'samplerate')

    def run(self, config: ConfigParser):
        self._get_parameter(config)

        input_path, input_filename = os.path.split(self.path)
        input_filename_short = os.path.splitext(input_filename)[0]

        if self.video_output == '':
            output_file = os.path.join(input_path, f'[encoded]{input_filename_short}.{self.video_output_format}')
        else:
            output_file = os.path.join(self.video_output, f'[encoded]{input_filename_short}.{self.video_output_format}')

        # 命令

        # 提取章节到temp
        has_chapter = False
        if self.video_chapter_copy:
            has_chapter = extract_chapter(self.ffmpeg_path, self.mkvextract_path, self.path, self.章节文件缓存)

        # vspipe
        cmd = [f'{self.vs_vsPipe_path}', '--y4m', f'{Vpy.destination_file}', '-', '|']
        # ffmpeg
        ffmpeg_cmd = [f'{self.ffmpeg_path}', '-f', 'yuv4mpegpipe',
                      '-i', 'pipe:',
                      '-i', f'{self.path}',
                      '-map', '0:v', '-map', '1:a',
                      '-c:v', 'copy', '-c:a', 'copy',
                      '-f', 'nut', '-', '|']
        # nvencc
        nvencc_cmd = ['-i', '-', '-c', 'hevc', '--qvbr', f'{self.video_quality}',
                      '--preset', 'p7', '--lookahead', '12', '--output-depth', '10', '--profile', 'main10']
        if self.video_aq != '':
            nvencc_cmd.extend(['--aq', '--aq-strength', f'{self.video_aq}'])
        if self.video_chapter_copy and has_chapter:
            nvencc_cmd.extend(['--chapter', f'{self.章节文件缓存}'])
        if self.video_key_on_chapter and has_chapter:
            nvencc_cmd.extend(['--key-on-chapter'])

        # 判断是否添加音频
        if self.audio_codec == '':
            cmd.extend([f'{self.nvencc_path}', '--y4m'])
            cmd.extend(nvencc_cmd)
            cmd.extend(['-o', f'{output_file}'])
        else:
            cmd.extend(ffmpeg_cmd)
            cmd.extend([f'{self.nvencc_path}', '--avsw'])
            cmd.extend(nvencc_cmd)
            cmd.extend(['--audio-codec', f'{self.audio_codec}',
                        '--audio-bitrate', f'{self.audio_bitrate}',
                        '--audio-samplerate', f'{self.audio_samplerate}'])
            cmd.extend(['-o', f'{output_file}'])


        # 开始运行
        print(" ".join(cmd))
        subprocess.run(cmd, shell=True)

        # 删除临时文件
        os.remove(Vpy.destination_file)
        if  has_chapter:
            os.remove(self.章节文件缓存)
