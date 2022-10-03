from gtts import gTTS

import os
tts = gTTS(text='Please, raise your right arm 10% higher.', lang='en')
tts.save("good.mp3")
os.system("mpg321 good.mp3")
