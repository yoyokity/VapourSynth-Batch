import os
import subprocess
from fractions import Fraction


def _format_nero_timestamp(seconds: float) -> str:
    """将秒数格式化为 Nero 章节时间戳"""
    total_milliseconds = round(seconds * 1000)
    hours, remainder = divmod(total_milliseconds, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}'


def _parse_ffmetadata_chapters(metadata_text: str):
    """解析 ffmetadata 中的章节信息"""
    chapters = []
    chapter = None

    for raw_line in metadata_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line == '[CHAPTER]':
            if chapter:
                chapters.append(chapter)
            chapter = {
                'timebase': '1/1000',
                'start': '0',
                'title': ''
            }
            continue

        if chapter is None or '=' not in line:
            continue

        key, value = line.split('=', 1)
        if key == 'TIMEBASE':
            chapter['timebase'] = value
        elif key == 'START':
            chapter['start'] = value
        elif key == 'title':
            chapter['title'] = value

    if chapter:
        chapters.append(chapter)

    return chapters


def extract_chapter(ffmpeg_path: str, mkvextract_path: str, input_file: str, output_file: str) -> bool:
    """提取章节文件，返回是否成功提取到章节"""

    if input_file.lower().endswith('.mkv'):
        # 处理 mkv 文件
        cmd = [
            f'{mkvextract_path}',
            f'{input_file}',
            'chapters',
            f'{output_file}'
        ]

        print(' '.join(cmd))
        subprocess.run(cmd, shell=True)

        # 检查是否生成了章节文件且文件不为空
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return True
        else:
            # 如果没有章节，删除空文件（如果有）并返回 False
            if os.path.exists(output_file):
                os.remove(output_file)
            return False
    else:
        # 处理其他格式的文件
        cmd = [
            f'{ffmpeg_path}',
            '-i', f'{input_file}',
            '-f', 'ffmetadata',
            '-'
        ]

        print(' '.join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        chapters = _parse_ffmetadata_chapters(result.stdout)

        if not chapters:
            return False

        with open(output_file, 'w', encoding='utf-8') as file:
            for index, chapter in enumerate(chapters, start=1):
                timebase = Fraction(chapter['timebase'])
                start = int(chapter['start'])
                timestamp = _format_nero_timestamp(float(start * timebase))
                title = chapter['title'] if chapter['title'] else f'Chapter {index:02d}'

                file.write(f'CHAPTER{index:02d}={timestamp}\n')
                file.write(f'CHAPTER{index:02d}NAME={title}\n')

        return True
