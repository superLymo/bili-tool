import aiohttp
import asyncio
import pathlib
import urllib.parse
from bilibili_api import emoji, Credential
import aiofiles

from utils import config_loader


async def download_one(
    session: aiohttp.ClientSession, url: str, filename: str, saveFolder: pathlib.Path
) -> bool:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54",
        "Referer": url,
    }

    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                # 使用aiofiles异步写入文件
                async with aiofiles.open(saveFolder / filename, "wb") as f:
                    await f.write(await response.read())

                print(f"✅ 图片已保存：{filename}")
                return True
            else:
                print(f"⚠️ 下载失败，状态码：{response.status} - {url}")
                return False
    except Exception as e:
        print(f"❌ 下载错误：{e} - {url}")
        return False


async def download_all_images(
    url_list: list[tuple[str, str]], saveFolder: pathlib.Path
) -> None:
    saveFolder.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        tasks = [
            download_one(session, url, filename, saveFolder)
            for url, filename in url_list
        ]

        await asyncio.gather(*tasks)


async def downloadPkg(pkgId: int, savePath: pathlib.Path):
    url_list = []

    detail = await emoji.get_emoji_detail(pkgId)

    for emj in detail["packages"][0]["emote"]:
        # 统一处理逻辑，优先使用gif_url
        url = emj.get("gif_url") or emj.get("url")
        if not url:
            continue

        # 清理URL（移除@后的参数）
        clean_url = url.split("@")[0]
        # 获取文件后缀
        suffix = pathlib.Path(urllib.parse.urlparse(clean_url).path).suffix
        # 安全的文件名处理
        safe_text = "".join(
            c for c in emj["text"] if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        filename = f"{safe_text}{suffix}"

        url_list.append((clean_url, filename))

    print(f"📥 共找到 {len(url_list)} 个表情")

    # 批量下载所有图片
    if url_list:
        await download_all_images(url_list, savePath)
        print("🎉 所有下载任务完成！")
    else:
        print("⚠️ 没有找到可下载的表情链接")


async def getAllEmojiPackages():
    credi = Credential(
        sessdata=config_loader.userConf.getSessData(),
        bili_jct=config_loader.userConf.getBiliJct(),
    )

    return await emoji.get_all_emoji(credential=credi)


async def searchMatchEmoji(emojiPackages: dict, emojiName: str):
    def search():
        matchList = []

        for pkg in emojiPackages["all_packages"]:
            if emojiName.lower() in pkg["text"].lower():
                matchList.append(pkg)

        return matchList

    return await asyncio.to_thread(search)
