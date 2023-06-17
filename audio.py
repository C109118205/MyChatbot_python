import pyaudio
import wave
from google.cloud import speech
from google.cloud import texttospeech
import openai

import time
from pygame import mixer


openai.api_key = 'your'r openai key'
client = speech.SpeechClient.from_service_account_file('key.json')


# 錄音參數設定
sample_format = pyaudio.paInt16
channels = 1
sample_rate = 44100
chunk_size = 1024
record_seconds = 5
output_filename = "output.wav"

# 初始化PyAudio物件
audio = pyaudio.PyAudio()

# 打開音頻串流
stream = audio.open(format=sample_format,
                    channels=channels,
                    rate=sample_rate,
                    frames_per_buffer=chunk_size,
                    input=True)

print("請開始說話...")

frames = []

# 錄音
for i in range(int(sample_rate / chunk_size * record_seconds)):
    data = stream.read(chunk_size)
    frames.append(data)


print("停...")

# 停止錄音
stream.stop_stream()
stream.close()
audio.terminate()

# 將錄製的音頻保存到檔案中
wave_file = wave.open(output_filename, 'wb')
wave_file.setnchannels(channels)
wave_file.setsampwidth(audio.get_sample_size(sample_format))
wave_file.setframerate(sample_rate)
wave_file.writeframes(b''.join(frames))
wave_file.close()

# print("音頻檔案已保存為：{}".format(output_filename))
transcript = ''

def transcribe_speech(audio_file_path):

    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        # language_code="zh-TW",
        language_code="en-us",
    )

    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        transcript = result.alternatives[0].transcript
        print("User say: {}".format(result.alternatives[0].transcript))
    prompt = transcript
    try:
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            print("GPT say:", response.choices[0].message.content)
            output_text = response.choices[0].message.content
            TTS(output_text)
            # 測試播放
            audio_file = 'output.mp3'  # 您要播放的 .mp3 檔案路徑

    except Exception as e:
            print("API Key is invalid or an error occurred.")
            print("Error:", str(e))

def play_sound():
    # pygame.init()
    mixer.init()

    sound = mixer.Sound('output.mp3')
    sound_length = sound.get_length()  # 音頻的長度（秒）
    sound.play()

    time.sleep(sound_length)

def TTS(output_text):
    client = texttospeech.TextToSpeechClient.from_service_account_json('key.json')
    voice_params = texttospeech.VoiceSelectionParams(
        language_code='en-US', ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    # 轉換文本為語音
    response = client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=output_text),
        voice=voice_params,
        audio_config=audio_config
    )
    # 將語音資料寫入檔案
    output_file = 'output.mp3'
    with open(output_file, 'wb') as audio_file:
        audio_file.write(response.audio_content)
    # print("TTS completed. The output is saved as '{}'.".format(output_file))
    play_sound()


transcribe_speech(output_filename)









