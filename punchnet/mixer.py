import pyaudio
import wave
import sys
import threading


# Sound mixer singleton
class Mixer:

    # Sounds map path -> sound
    SOUNDS = {}
    
    @staticmethod
    def load(path):
        if path in Mixer.SOUNDS:
            return Mixer.SOUNDS[path]
        try:
            wf = wave.open(path, 'rb')
            chunk_size = 1024
            data = []
            while True:
                chunk = wf.readframes(chunk_size)
                if not chunk:
                    break
                data.append(chunk)
            wf.close()
            sound = lambda : None
            setattr(sound, 'data', data)
            setattr(sound, 'sampwidth', wf.getsampwidth())
            setattr(sound, 'channels', wf.getnchannels())
            setattr(sound, 'framerate', wf.getframerate())
            Mixer.SOUNDS[path] = sound
            return sound
        except IOError as ioe:
            print 'Missing sound: ' + path
        return None
    
    @staticmethod
    def play(path):
        def play_loop(sound):
            audio = pyaudio.PyAudio()
            stream = audio.open(format = audio.get_format_from_width(sound.sampwidth),
                            channels = sound.channels,
                            rate = sound.framerate,
                            output = True)
            for chunk in sound.data:
                stream.write(chunk)
            stream.stop_stream()
            stream.close()
            audio.terminate()
        sound = Mixer.load(path)
        if sound:
            thread = threading.Thread(target = play_loop, args = [sound])
            thread.start() 
        