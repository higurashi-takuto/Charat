import os
import requests
import json
import wave
import pyaudio
from mlask import MLAsk

APIKEY = ''


def chat(input_word, mode):
    url = 'https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue?APIKEY={}'.format(
        APIKEY)

    payload = {'utt': input_word,
               'context': '',
               'mode': mode
               }

    r = requests.post(url, data=json.dumps(payload))
    data = r.json()

    return data


def voice(input_voice):
    url = 'https://api.apigw.smt.docomo.ne.jp/amiVoice/v1/recognize?APIKEY={}'.format(
        APIKEY)

    files = {"a": open(input_voice, 'rb'), "v": "on"}

    r = requests.post(url, files=files)
    data = r.json()
    response = data['text']
    return response


def emotion(input_word):
    emotion_analyzer = MLAsk()
    response = emotion_analyzer.analyze(input_word)
    if 'orientation' in response:
        return response['orientation']
    return 'NONE'


def audioIndex():
    p = pyaudio.PyAudio()
    count = p.get_device_count()
    devices = []
    for i in range(count):
        devices.append(p.get_device_info_by_index(i))

    for i, dev in enumerate(devices):
        print(i, dev['name'])


def audioSave():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1  # モノラル
    RATE = 16000  # サンプルレート
    CHUNK = 2**11  # データ点数
    RECORD_SECONDS = 3  # 録音する時間の長さ
    WAVE_OUTPUT_FILENAME = "voice.wav"
    INDEX = 0

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        input_device_index=INDEX,
                        frames_per_buffer=CHUNK)

    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    return WAVE_OUTPUT_FILENAME


def recWord():
    voice_path = audioSave()
    r = voice(voice_path)
    os.remove(voice_path)
    return r


def response(input_word, mode):
    r = chat(input_word, mode)
    response = {'utt': r['utt'],
                'mode': r['mode'],
                'emotion': emotion(r['utt'])
                }
    return response


def convText(word, length):
    if length < len(word):
        text = ''
        for char in [word[i:i + length] for i in range(0, len(word), length)]:
            text = text + char + '\n'
    else:
        text = word
    return text
