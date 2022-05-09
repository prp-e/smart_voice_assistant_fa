import json
import os
import queue
import sounddevice as sd
import vosk
import sys


samplerate = None
q = queue.Queue()
dump_fn = None
default_device = sd.default.device[0]

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


model = "model"
if not os.path.exists(model):
    print ("Please download a model for your language from https://alphacephei.com/vosk/models")
    print ("and unpack as 'model' in the current folder.")
if samplerate is None:
    device_info = sd.query_devices(default_device, 'input')
    # soundfile expects an int, sounddevice provides a float:
    samplerate = int(device_info['default_samplerate'])

    model = vosk.Model(model)

    with sd.RawInputStream(samplerate=samplerate, blocksize = 8000, device=default_device, dtype='int16',
        channels=1, callback=callback):
        print('#' * 80)
        print('Press Ctrl+C to stop the recording')
        print('#' * 80)

        rec = vosk.KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                saying = json.loads(rec.Result())
                print(saying)
                if saying['text'] == "سلام":
                    os.system(f'espeak -p 45 -s 140 -v mb-ir1 سلام')
                if saying['text'] == "راهنمایی":
                    os.system('espeak -p 45 -s 140 -v mb-ir1 "مَن یک دَستیارِ صوتیِ هوشمَند هَستَم."')
                if saying['text'] == 'خداحافظ':
                    os.system('espeak -p 45 -s 140 -v mb-ir1 خُداحافِظ')
                    exit()
            else:
                pass
            if dump_fn is not None:
                dump_fn.write(data)

