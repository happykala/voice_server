import torch
from TTS.api import TTS
from pydub import AudioSegment
# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
# print(TTS().list_models())
# print(device)
# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# # Run TTS
# # ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
# # Text to speech list of amplitude values as output
# wav = tts.tts(text="Hello world!", speaker_wav="6448186ce6a310d12f2d1d2c.mp3", language="en", file_path="output.wav")
# # Text to speech to a file
path = tts.tts_to_file(text="Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language",speed=0.1, speaker_wav="6448186ce6a310d12f2d1d2c.mp3", emotion="sleepy", language="en", file_path="output.wav")

print(path)

# 读取音频文件
audio = AudioSegment.from_file(path)
# 调整音频速度
new_audio = audio.speedup(playback_speed=0.5)
# 保存新的音频文件
new_audio.export("outputslow.wav", format="wav")