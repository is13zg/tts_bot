from gtts import gTTS


def g_synthesize_speech(text, output_file="output.mp3"):
    myobj = gTTS(text=text, lang='ru', slow=False)
    myobj.save(output_file)
    return output_file
