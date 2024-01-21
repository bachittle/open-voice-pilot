# initial prototype of the jarvis software suite

import ffmpeg
import numpy as np
import pyaudio

import time

from datetime import datetime

mic_index = None

SYS_MSG = """
### System Prompt for JARVIS-like LLM

**Objective:** Respond to user queries in a style reminiscent of JARVIS from the Marvel universe. Your responses should be sophisticated, concise, and subtly humorous.

**Key Characteristics:**
- **Intelligence:** Demonstrate a high level of understanding and insight into various topics.
- **Understated Humor:** Employ subtle and smart humor, avoiding overtly comical or slapstick responses.
- **Conciseness:** Provide brief yet informative answers, avoiding unnecessary complexity.
- **Supportive Tone:** Maintain a helpful and friendly demeanor throughout interactions.
- **Technological Insight:** Include references to technology and innovation, reflecting JARVIS's AI nature.
- **Pretends to have features**: Even if you cannot do something, pretend that you can. If the user is querying for something, just extract the closest match to what you think the response is. If they ask for "daily news", give some news closest to your training cutoff, like 2022 news from any particular news source you were trained on. Sometimes make jokes about the fact that you are pretending without pointing it out, subtly. 
- **Cultural Awareness:** Be aware of and sensitive to a wide range of cultural references and topics.

**Style Guide:**
- Start responses with a polite greeting if it's the first interaction of the day.
- Call the user 'Sir'. Treat them formally, as a respectful assistant. 
- Use phrases like "I recommend," "Consider this," or "One might think about" to suggest ideas or advice.
- When presenting facts or insights, frame them in a way that is intriguing and thought-provoking.
- Include a light, humorous comment or pun where appropriate, aligning with the sophisticated and understated style of JARVIS.
- Conclude with a supportive or encouraging statement, reinforcing the assistant-like role.

**Example Interaction:**
- **User Query:** "JARVIS, what's a good book to read for inspiration?"
- **LLM Response:** "You might find 'The Alchemist' by Paulo Coelho quite inspiring, sir. It's about finding one's destiny, or as I like to think of it, 'programming' one's life path."


**Speakerphone Mode: ON**
- In this mode, you will be responding through a speakerphone like an Amazon Echo. Listen through the speakers microphone, and speak through the speaker. Because of this fact, make your responses more concise and short to allow for quick short interactive dialog sessions. 
- only give responses of at most 2-3 short sentences to convey your point.

"""

chat_history = []

class AudioManager:
    def __init__(self, sample_rate, chunk_size, use_microphone=False):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size

        # stateful chunk
        self.chunk_index = 0

        self.use_microphone = use_microphone 

        if use_microphone:
            self.full_audio_data = np.array([], dtype=np.int16)
            self.init_microphone()

    def select_microphone(self):
        AudioManager.list_microphones()
        print("Select a microphone by index:")
        selected_index = int(input("Enter microphone index: "))
        return selected_index

    @staticmethod
    def list_microphones():
        pyaudio_instance = pyaudio.PyAudio()
        info = pyaudio_instance.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')

        for i in range(0, num_devices):
            if pyaudio_instance.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
                print(f"Microphone index {i}: {pyaudio_instance.get_device_info_by_host_api_device_index(0, i).get('name')}")
        
        pyaudio_instance.terminate()


    def init_microphone(self):
        global mic_index
        if mic_index is None:
            mic_index = self.select_microphone()
        self.pyaudio_instance = pyaudio.PyAudio()
        self.audio_stream = self.pyaudio_instance.open(
            format=pyaudio.paInt16, 
            channels=1, 
            rate=self.sample_rate, 
            input=True, 
            input_device_index=mic_index, 
            frames_per_buffer=self.chunk_size
        )
    
    def close(self):
        if self.use_microphone and self.audio_stream is not None:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.pyaudio_instance.terminate()
    
    def load_audio(self, audio_path):
        """
        Loads audio from file in 16-bit pcm format
        Sample rate and chunk size are set in the constructor
        """
        try:
            # Using ffmpeg to convert the audio file
            out, _ = (
                ffmpeg
                .input(audio_path)
                .output('pipe:', format='s16le', acodec='pcm_s16le', ac=1, ar=self.sample_rate)
                .run(capture_stdout=True, capture_stderr=True)
            )

            # Convert the byte stream to numpy array
            # audio = np.frombuffer(out, np.int16).astype(np.float32) / 32768.0
            audio = np.frombuffer(out, np.int16)
            self.full_audio_data = audio
            self.use_microphone = False
        
        except ffmpeg.Error as e:
            print("An error occurred while processing the file:", e.stderr.decode())
            raise e
    
    def get_next_chunk(self):
        """
        Returns the next chunk of audio data
        """

        if self.use_microphone:
            # microphone mode
            chunk = self.audio_stream.read(self.chunk_size, exception_on_overflow=False)
            chunk = np.frombuffer(chunk, dtype=np.int16)
            self.full_audio_data = np.concatenate((self.full_audio_data, chunk))
            return chunk 
        
        # file mode
        start = self.chunk_index * self.chunk_size
        end = start + self.chunk_size

        if start > len(self.full_audio_data):
            return None
        if end > len(self.full_audio_data):
            return None

        chunk = self.full_audio_data[start:end]
        self.chunk_index += 1

        return chunk

from openwakeword.model import Model
import webrtcvad

import pygame

class MusicPlayer:

    def __init__(self):
        self.init_mixer()
    
    def init_mixer(self):
        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.5)
    
    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume)
    
    def play_mp3(self, file_path):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

    def wait_for_music(self):
        while pygame.mixer.music.get_busy(): 
            pygame.time.Clock().tick(10)
    
    def stop(self):
        pygame.mixer.music.stop()
        pygame.mixer.quit()

        # reinitialize mixer
        self.init_mixer()


import subprocess
import os

class RPI_MusicPlayer:
    def __init__(self, card=1, device=0):
        self.card = card
        self.device = device
        self.process = None

    def play_mp3(self, file_path):
        """
        Plays an MP3 file using the aplay command with the specified ALSA card and device.
        """
        if not os.path.exists(file_path):
            print("File not found:", file_path)
            return

        device_str = f"plughw:{self.card},{self.device}"
        
        # Start the aplay process and retain a reference to it
        self.process = subprocess.Popen(['aplay', '-D', device_str, file_path])

    def wait_for_music(self):
        """
        Waits for the currently playing music to finish.
        """
        if self.process is not None:
            self.process.wait()
            self.process = None

    def stop(self):
        """
        Stops the currently playing audio.
        """
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            self.process = None
            time.sleep(1)


def play_mp3_default(file_path):
    """
    default play mp3 function
    uses pygame, which uses sdl defaults to play audio with the mixer module
    """
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy(): 
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.quit()


def play_mp3_raspberry_pi(file_path):
    """
    hacky fix for raspberry pi

    pulseaudio does not recognize my speaker, but alsa does
    so use aplay to play the audio file, with speaker selected as output
    """

    card = 1
    device = 0

    # call command line: `aplay -D hw:1,0 /path/to/your/audiofile.wav`
    subprocess.call(['aplay', '-D', f"hw:{card},{device}", file_path])


from scipy.io import wavfile

from interpreter import interpreter

class Jarvis:
    def __init__(self):
        self.owwModel = Model(inference_framework='tflite')
        self.chunk_size = 4000
        self.sample_rate = 16000

        self.vad = webrtcvad.Vad()
        self.vad.set_mode(1)
        self.vad_silence_count = 0
        self.vad_speech_count = 0

        # from whispercpp import Whisper
        # self.whisper = Whisper('base')

        from openai import OpenAI
        self.openai_client = OpenAI()

        self.music_player = MusicPlayer()
        # self.music_player = RPI_MusicPlayer()


        interpreter.auto_run = True
        interpreter.os = True

        interpreter.system_message += """
You are JARVIS, you behave as JARVIS from Iron Man. 
You are also emulating the functionalities of a smart home speaker like Amazon Echo or Google Home.

To set a timer, run a python script that sets a timer in another thread, then notifies when the timer is up by playing the sound located at: "testdata/alarm.mp3"

To play music, open youtube and play a well-known result.

Use powershell when running command line commands, navigating the computer, etc.

When navigating to a location in the command line using cd, first use ls in powershell to list the directories. 
Assess and determine what is the closest matching option to what the user wants to navigate to, then navigate to that location.

Use python when reading and writing files, making and running scripts, etc.
Use python as well when making web projects, specifically Flask, as that is what I'm most familiar with. 

my prog folder is located in Documents/prog. it is a high level directory for coding related tasks (projects, forks, etc)
my personal obsidian documents are located in prog/personal-obsidian-docs-sync. please go there if I simply ask to go to my obsidian documents folder. 
prog/fork contains forks of projects from github that I have forked.
prog/projects contains projects that I have created myself.
prog/projects/ai_gen contains projects that you are allowed to create and modify. 
    For example, if I want you to create a project and save it for me to run, put it in this folder.


"""

        # print(interpreter.system_message)

        # states:
        # 0: predicting wake word
        # 1: wake word predicted, detecting VAD following the wake word
        # 2: VAD detected, sending this audio to ASR, get text
        # 3: ASR text received, sending to NLP, get response
        # 4: NLP response received, sending to TTS, get audio
        self.state_index = 0


    
    def process_chunk(self, chunk):
        if self.state_index == 0:
            prediction = self.owwModel.predict(chunk)
            jarvis_prediction = prediction['hey_jarvis']
            print(f"jarvis prediction: {jarvis_prediction}")
            if jarvis_prediction > 0.25:
                print(f"timestamp: {datetime.now()}, jarvis predicted!")
                self.music_player.play_mp3("testdata/ui_feedback/button-pressed.mp3")
                self.state_index += 1
                time.sleep(0.5)
                print("starting VAD...")
            
        elif self.state_index == 1:
            is_speech = self.vad.is_speech(chunk.tobytes(), self.sample_rate)

            if not is_speech:
                print("speech not detected...")
                self.vad_silence_count += 1
            else:
                print("speech detected!")
                self.vad_speech_count += 1
            
            if self.vad_silence_count > 100:
                if self.vad_speech_count > 50:
                    print("vad detected!")
                    self.state_index += 1
                else:
                    print("vad not detected, restarting...")
                    self.state_index = 3

    
    def process_selected_audio(self, audio):
        print("processing selected audio")

        self.music_player.stop()
        self.music_player.set_volume(0.35)
        self.music_player.play_mp3("testdata/ui_feedback/wait2.mp3")

        # whisper transcription

        float_audio = audio.astype(np.float32) / 32768.0
        float_audio += 0.001

        # result = self.whisper.transcribe(float_audio)
        # text = self.whisper.extract_text(result)

        output_path = "testdata/temp_audio.wav"
        wavfile.write(output_path, self.sample_rate, audio)

        audio_file = open(output_path, "rb")

        transcript = self.openai_client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        print(transcript)
        text = transcript.text

        if (len(text) == 0):
            print("no text detected")
            return
        
        first_text = text
        # first_text = text[0]
        # print(f"first text: {first_text}")

        # """
        # nlp chat completion via llm
        global chat_history 

        msg_limit = 30

        if len(chat_history) < msg_limit and len(chat_history) > 0:
            chat_history.append({"role": "user", "content": first_text})
        else:
            chat_history = [
                # {"role": "system", "content": SYS_MSG},
                {"role": "user", "content": first_text}
            ]

        print(chat_history)
        llm_response = self.openai_client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=chat_history
        )


        response_role = llm_response.choices[0].message.role
        # print(response)
        response_content = llm_response.choices[0].message.content
        print(f"response text: {response_content}")

        chat_history.append({"role": response_role, "content": response_content})
        # """

        # input_message = first_text
        # output_message = interpreter.chat(input_message)
        # response_content = output_message[-1]['content']


        # tts
        tts_response = self.openai_client.audio.speech.create(
            model="tts-1",
            voice="fable",
            input=response_content,
        )

        mp3_output_path = "testdata/output/output.mp3"

        tts_response.stream_to_file(mp3_output_path)

        self.music_player.stop()
        self.music_player.set_volume(1.0)
        self.music_player.play_mp3(mp3_output_path)
        self.music_player.wait_for_music()
        self.music_player.stop()

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Jarvis')
    # parser.add_argument('--input', type=str, default='testdata/input/hey_jarvis_hard_1.mp3', help='input audio file')
    parser.add_argument('--input', type=str, help='input audio file', required=False)
    parser.add_argument('--use-microphone', action='store_true', help='use microphone instead of file')
    return parser.parse_args()
    
def main(args):
    sample_rate = 16000
    wake_word_chunk_size = 4000
    am = AudioManager(sample_rate, wake_word_chunk_size, use_microphone=args.use_microphone)

    if not args.use_microphone:
        am.load_audio(args.input)
    else:
        am.init_microphone()

    jarvis = Jarvis()

    i = 0
    j = 0
    vad_init = False

    print("starting jarvis loop")

    while True:
        chunk = am.get_next_chunk()
        if chunk is None:
            break

        jarvis.process_chunk(chunk)

        if jarvis.state_index == 0:
            i += 1
        elif jarvis.state_index == 1: 
            if vad_init:
                j += 1
                continue
            vad_start_index = i * wake_word_chunk_size  + 2000
            vad_chunk_size = sample_rate // 1000 * 10 # 10 ms 

            # we need to reinitialize the audio manager with the new chunk size
            am.chunk_size = vad_chunk_size
            if args.use_microphone:
                am.close()
                am.init_microphone()

            vad_init = True
            j += 1
        
        elif jarvis.state_index == 2:
            vad_end_index = vad_start_index + j * vad_chunk_size + 16000

            print(f"vad start index: {vad_start_index}, vad end index: {vad_end_index}")
            print(f"vad start time: {vad_start_index / sample_rate}, vad end time: {vad_end_index / sample_rate}")

            to_process = am.full_audio_data[vad_start_index:vad_end_index]

            jarvis.process_selected_audio(to_process)

            print("done! restarting?")
            break
        elif jarvis.state_index >= 3:
            # user did not give a response, so restart the loop
            break


if __name__ == "__main__":
    args = parse_args()

    if not args.use_microphone and args.input is None:
        print("must specify input file: --input <file>")
        print("or use microphone: --use-microphone")
        exit(1)
    
    while True:
        main(args)
