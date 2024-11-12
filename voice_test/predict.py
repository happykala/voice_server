# Prediction interface for Cog
from cog import BasePredictor, Input, Path
import os
from TTS.api import TTS
from typing import Any
import requests
import zipfile

class Predictor(BasePredictor):
    def setup(self) -> None:
        """Load the model into memory to make running multiple predictions efficient"""
        os.environ["COQUI_TOS_AGREED"] = "1"
        # 将这里的model替换为主动下载的模型路径，这样就不需要每次初始化的时候都需要下载了
        self.model = TTS(model_path='/home/model', config_path='/home/model/config.json').to('cuda')

    def download_and_extract_zip(self, url, save_folder, unzip=True):
        """
        从指定URL下载ZIP文件并解压到同名文件夹
        
        参数:
        url (str): ZIP文件的下载链接
        save_folder (str): 要保存ZIP文件的文件夹路径
        
        返回:
        str: 解压后的文件夹路径
        """
        # 确保保存文件夹存在
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # 获取文件名
        file_name = url.split("/")[-1]
        file_path = os.path.join(save_folder, file_name)

        # 拼接解压后的文件夹路径 (同名文件夹)
        extract_folder = os.path.join(save_folder, file_name.replace('.zip', ''))

        try:
            # 下载ZIP文件
            response = requests.get(url)
            # 检查请求是否成功
            if response.status_code == 200:
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f"ZIP File Saved: {file_path}")
                if unzip:
                    # v需要解压的时候才解压，解压ZIP文件到同名文件夹
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_folder)
                    print(f"File Unzip Path: {extract_folder}")
                    # 解压缩完毕之后删除压缩文件
                    os.remove(file_path)
                    return extract_folder
                else:
                    # 不需要解压的时候直接返回文件的名称即可
                    return file_path
            else:
                print("Download File Failed, Code Status:", response.status_code)
                return None
        except Exception as e:
            print(f"Download Error: {e}")
            return None
    def predict(
        self,
        text: str = Input(
            description="Text to synthesize",
            default="Hi there, I'm your new voice clone. Try your best to upload quality audio"
        ),
        speaker: str = Input(description="Original speaker audio url (wav, mp3, m4a, ogg, or flv). Duration should be at least 6 seconds."),
        language: str = Input(
            description="Output language for the synthesised speech",
            choices=["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh", "hu", "ko", "hi"],
            default="en"
        ),
        cleanup_voice: bool = Input(
            description="Whether to apply denoising to the speaker audio (microphone recordings)",
            default=False
        ),
    ) -> Any:
        """Run a single prediction on the model"""
        # 将用户的语音文件下载到本地，并做必要的处理
        audio_path_temp = self.download_and_extract_zip(speaker, './demo_file', False)
        speaker_wav = audio_path_temp
        filter = "highpass=75,lowpass=8000,"
        trim_silence = "areverse,silenceremove=start_periods=1:start_silence=0:start_threshold=0.02,areverse,silenceremove=start_periods=1:start_silence=0:start_threshold=0.02"
        # ffmpeg convert to wav and apply afftn denoise filter. y to overwrite and avoid caching
        if cleanup_voice:
            os.system(f"ffmpeg -i {speaker} -af {filter}{trim_silence} -y {speaker_wav}")
        else:
            os.system(f"ffmpeg -i {speaker} -y {speaker_wav}")

        path = self.model.tts_to_file(
            text=text, 
            file_path = "/tmp/output.wav",
            speaker_wav = speaker_wav,
            language = language
        )
        # 处理完毕，删除下载的音频文件
        os.remove(audio_path_temp)
        print("delete speaker audio temp success")
        return Path(path)