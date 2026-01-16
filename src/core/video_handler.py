import asyncio, pathlib, aiohttp, aiofiles, os
import bilibili_api as bapi

from utils import config_loader as conf


def getVideo(bvid: str) -> bapi.video.Video:
    credi = bapi.Credential(
        conf.userConf.getSessData(),
        conf.userConf.getBiliJct(),
        conf.userConf.getBuvid3(),
    )

    return bapi.video.Video(bvid=bvid, credential=credi)


async def getPageCount(vido: bapi.video.Video) -> int:
    return len(await vido.get_pages())


async def downloadVideoAss(vido: bapi.video.Video, folder: str) -> None:
    assRootPath = pathlib.Path(folder)

    if not assRootPath.exists():
        assRootPath.mkdir(parents=True, exist_ok=True)

    assTasks = [
        bapi.ass.make_ass_file_danmakus_protobuf(
            obj=vido, page=pageIndex, out=f"./{folder}/{pageIndex}.ass"
        )
        for pageIndex in range(await getPageCount(vido))
    ]

    await asyncio.gather(*assTasks, return_exceptions=True)


async def download(url: str, out: str, intro: str):
    dwn_id = await bapi.get_client().download_create(url, bapi.HEADERS)
    bts = 0
    tot = bapi.get_client().download_content_length(dwn_id)
    with open(out, "wb") as file:
        while True:
            bts += file.write(await bapi.get_client().download_chunk(dwn_id))
            print(f"{intro} - {out} [{bts} / {tot}]", end="\r")
            if bts == tot:
                break


async def downloadOneVideo(downloadData: dict, folderPath: pathlib.Path) -> None:
    if not folderPath.exists():
        folderPath.mkdir(parents=True, exist_ok=True)

    folder = str(folderPath)

    detecter = bapi.video.VideoDownloadURLDataDetecter(data=downloadData)
    streams = detecter.detect_best_streams()
    # 有 MP4 流 / FLV 流两种可能
    if detecter.check_flv_mp4_stream():
        # FLV 流下载
        await download(streams[0].url, f"{folder}/flv_temp.flv", "下载 FLV 音视频流")
        # 转换文件格式
        os.system(
            f"{conf.userConf.getFfmpeg()} -i {folder}/flv_temp.flv {folder}/video.mp4"
        )
        # 删除临时文件
        os.remove(f"{folder}/flv_temp.flv")
    else:
        # MP4 流下载
        await download(streams[0].url, f"{folder}/video_temp.m4s", "下载视频流")
        await download(streams[1].url, f"{folder}/audio_temp.m4s", "下载音频流")
        # 混流
        os.system(
            f"{conf.userConf.getFfmpeg()} -i {folder}/video_temp.m4s -i {folder}/audio_temp.m4s -vcodec copy -acodec copy {folder}/video.mp4"
        )
        # 删除临时文件
        os.remove(f"{folder}/video_temp.m4s")
        os.remove(f"{folder}/audio_temp.m4s")

    print(f"已下载为：{folder}/video.mp4")


async def downloadVideos(vido: bapi.video.Video, folder: pathlib.Path) -> None:
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)

    vidoTasks = [
        downloadOneVideo(
            await vido.get_download_url(pageIndex), folder / str(pageIndex)
        )
        for pageIndex in range(await getPageCount(vido))
    ]

    await asyncio.gather(*vidoTasks, return_exceptions=True)


async def downloadVideosV2(vido: bapi.video.Video, folder: pathlib.Path) -> None:
    if conf.userConf.getFfmpeg() == "" or not pathlib.Path(conf.userConf.getFfmpeg()).exists():
        print("没找到ffmpeg~")

        return

    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)

    for pageIndex in range(await getPageCount(vido)):
        await downloadOneVideo(
            await vido.get_download_url(pageIndex), folder / str(pageIndex)
        )
