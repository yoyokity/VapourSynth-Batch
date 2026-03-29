# 使用说明

本工具的使用方式很简单，按下面顺序操作即可。

## 0. 使用 uv 安装环境

建议先安装 `uv`：

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

然后在项目目录创建venv虚拟环境：

```bash
uv venv
```



## 1. 提前安装 VapourSynth

使用前请先安装VapourSynth 工具包：

https://github.com/AmusementClub/tools/releases

请下载并安装 `vapoursynth_cpu+cuda` 版本。

安装完成后，在 `配置参数.ini` 中把 `VSPipe_path` 修改为你本机 `VSPipe.exe` 的实际路径。



## 2. 修改编码相关参数

编码相关参数在 `配置参数.ini` 中修改。

可根据需要调整的内容包括：

- 输出路径
- 输出格式
- 画质参数
- 音频编码
- 音频码率
- VSPipe 路径
- vpy 文件路径



## 3. 修改视频修复相关参数

视频修复、滤镜处理相关参数在 `vpy文件.py` 中修改。

可根据需要在脚本中调整：

- 降噪
- 去色带
- 抗锯齿
- 锐化
- 其他 VapourSynth 处理参数



## 4. 开始处理视频

把需要处理的视频文件直接拖到 `将一个或多个视频文件拖上来.bat` 上即可开始处理。

支持一次拖入一个或多个视频文件。
