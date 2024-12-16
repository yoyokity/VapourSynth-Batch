import vapoursynth as vs
import havsfunc as haf
import mvsfunc as mvf
import adjust

core = vs.core

video_src = r"$FILE_PATH$"

core.max_cache_size = 9000  # 内存
video = core.lsmas.LWLibavSource(video_src, format="yuv420p16")


#改变大小
#video = core.resize.Spline36(video, 1920, 1080)


# 预降噪
video = core.nlm_cuda.NLMeans(video, d=0, wmode=3, h=7)


if True:
	# 去色带
    video = core.neo_f3kdb.Deband(video, range=12, y=60, cb=24, cr=24, grainy=0, grainc=0, output_depth=16)
    video = core.neo_f3kdb.Deband(video, range=24, y=40, cb=16, cr=16, grainy=0, grainc=0, output_depth=16)
    

    # 去锯齿
    def aa_eedi2(clip):
        """适用于比较糊的源"""
        w = clip.width
        h = clip.height
        aa_clip = core.std.ShufflePlanes(clip, 0, vs.GRAY)
        aa_clip = core.eedi2.EEDI2(aa_clip, field=1, mthresh=10, lthresh=20, vthresh=20, maxd=24, nt=50)
        aa_clip = core.fmtc.resample(aa_clip, w, h, 0, -0.5).std.Transpose()
        aa_clip = core.eedi2.EEDI2(aa_clip, field=1, mthresh=10, lthresh=20, vthresh=20, maxd=24, nt=50)
        aa_clip = core.fmtc.resample(aa_clip, h, w, 0, -0.5).std.Transpose()
        aaed = core.std.ShufflePlanes([aa_clip, clip], [0, 1, 2], vs.YUV)
        aaed = core.rgvs.Repair(aaed, clip, 2)
        return aaed


    def aa_nnedi3(clip):
        """适用于分辨率比较高的源"""
        w = clip.width
        h = clip.height
        aa_clip = core.std.ShufflePlanes(clip, 0, vs.GRAY)
        aa_clip = core.znedi3.nnedi3(aa_clip, field=1, dh=True, nsize=3, nns=2, qual=2)
        aa_clip = core.fmtc.resample(aa_clip, w, h, 0, -0.5).std.Transpose()
        aa_clip = core.znedi3.nnedi3(aa_clip, field=1, dh=True, nsize=3, nns=2, qual=2)
        aa_clip = core.fmtc.resample(aa_clip, h, w, 0, -0.5).std.Transpose()
        aaed = core.std.ShufflePlanes([aa_clip, clip], [0, 1, 2], vs.YUV)
        aaed = core.rgvs.Repair(aaed, clip, 2)
        return aaed


    def aa(clip):
        """强力抗锯齿"""
        w = clip.width
        h = clip.height
        uw = w * 3 // 2
        uh = h * 3 // 2
        dw = w * 3 // 4
        dh = h * 3 // 4
        aa_clip = core.fmtc.resample(clip, dw, dh)
        aa_clip = core.eedi2.EEDI2(aa_clip, field=1)
        aa_clip = core.fmtc.resample(aa_clip, w, uh, sy=[-0.5, -1]).std.Transpose()
        aa_clip = core.eedi2.EEDI2(aa_clip, field=1)
        aa_clip = core.fmtc.resample(aa_clip, uh, uw, sy=[-0.5, -1]).fmtc.bitdepth(bits=8)
        aa_clip = core.sangnom.SangNom(aa_clip, aa=48, dh=False).std.Transpose()
        aa_clip = core.sangnom.SangNom(aa_clip, aa=48, dh=False)
        aa_clip = core.fmtc.resample(aa_clip, clip.width, clip.height)
        aa_clip = core.rgvs.Repair(aa_clip, clip, 2)
        return aa_clip


    video = aa_eedi2(video)

    # 锐化
    video = core.cas.CAS(video, sharpness=0.7)

# 输出
video.set_output(0)
