import pathlib
import asyncio
import aiohttp

from utils import config_loader


def genTtsPostJson(targetText : str, targetLang : str = "zh") -> dict:
    return {
        "text": targetText,
        "text_lang": targetLang,
        "ref_audio_path": config_loader.userConf.getRefAudio(),
        "aux_ref_audio_paths": [],
        "prompt_lang": config_loader.userConf.getRefAudioLang(),
        "prompt_text": config_loader.userConf.getRefAudioText(),
        "top_k": 5,
        "top_p": 1,
        "temperature": 1,
        "text_split_method": "cut5",
        "batch_size": 1,
        "batch_threshold": 0.75,
        "split_bucket": True,
        "speed_factor": 1,
        "fragment_interval": 0.3,
        "seed": -1,
        "media_type": "wav",
        "streaming_mode": False,
        "parallel_infer": True,
        "repetition_penalty": 1.35,
        "sample_steps": 32,
        "super_sampling": False,
        "overlap_length": 2,
        "min_chunk_length": 16,
    }


async def _changeGptModel(sess: aiohttp.ClientSession, gptPath: pathlib.Path) -> bool:
    try:
        async with sess.get(
            config_loader.userConf.getSovitsApiServer() + "/set_gpt_weights"
        ) as resp:
            if resp.status != 200:
                return False

            return True
    except Exception as e:
        print(e)

    return False


async def _changeSovitsModel(
    sess: aiohttp.ClientSession, sovitsPath: pathlib.Path
) -> bool:
    try:
        async with sess.get(
            config_loader.userConf.getSovitsApiServer() + "/set_sovits_weights"
        ) as resp:
            if resp.status != 200:
                return False

            return True
    except Exception as e:
        print(e)

    return False


async def changeSpeaker(
    sess: aiohttp.ClientSession, gptPath: pathlib.Path, sovitsPath: pathlib.Path
) -> bool:
    changeTasks = [_changeGptModel(sess, gptPath), _changeSovitsModel(sess, sovitsPath)]

    changeResult = await asyncio.gather(*changeTasks)

    return changeResult[0] and changeResult[1]
