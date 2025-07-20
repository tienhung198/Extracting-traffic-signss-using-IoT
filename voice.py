from gtts import gTTS
import io
from pygame import mixer


def text_to_speech_gtts(text, lang='vi'):
    # Chuyển đổi văn bản thành giọng nói
    tts = gTTS(text=text, lang=lang, slow=False)

    # Lưu âm thanh vào bộ nhớ
    audio_file = io.BytesIO()
    tts.write_to_fp(audio_file)

    # Phát âm thanh
    audio_file.seek(0)  # Di chuyển con trỏ về đầu
    mixer.init()
    mixer.music.load(audio_file)
    mixer.music.play()

    # Chờ cho đến khi việc phát xong
    while mixer.music.get_busy():
        pass



