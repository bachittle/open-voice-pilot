from abc import ABC, abstractmethod
import pyaudio
import numpy as np
import ffmpeg

# Abstract Class
class AudioProcessor(ABC):
    @abstractmethod
    def read_chunk(self):
        pass

    @abstractmethod
    def close(self):
        pass

class FileAudioProcessor(AudioProcessor):
    def __init__(self, filepath, chunk_size=1024):
        self.chunk_size = chunk_size
        self.filepath = filepath
        out, _ = (
            ffmpeg.input(filepath)
            .output("pipe:", format='wav')
            .run(capture_stdout=True, capture_stderr=True)
        )

        self.audio = np.frombuffer(out, np.int16)
        self.chunk_index = 0

    def read_chunk(self):
        start = self.chunk_index * self.chunk_size
        end = start + self.chunk_size

        if start >= len(self.audio):
            return None
        
        if end > len(self.audio):
            end = len(self.audio)

        chunk = self.audio[start:end]
        self.chunk_index += 1
        return chunk
    
    def close(self):
        pass


def list_microphones():
    pyaudio_instance = pyaudio.PyAudio()
    info = pyaudio_instance.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')

    for i in range(0, num_devices):
        if pyaudio_instance.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
            print(f"Microphone index {i}: {pyaudio_instance.get_device_info_by_host_api_device_index(0, i).get('name')}")
    
    pyaudio_instance.terminate()

def select_microphone():
    list_microphones()
    index = int(input("Select microphone index: "))
    return index

# Microphone Audio Processor
class MicrophoneAudioProcessor(AudioProcessor):
    def __init__(self, device_index=None, chunk_size=1024, format=pyaudio.paInt16, channels=1, rate=44100):
        self.chunk_size = chunk_size
        self.format = format
        self.channels = channels
        self.rate = rate
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format, channels=self.channels, rate=self.rate, input=True, input_device_index=device_index, frames_per_buffer=self.chunk_size)

    def read_chunk(self):
        data = self.stream.read(self.chunk_size, exception_on_overflow=False)
        return np.frombuffer(data, dtype=np.int16)

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()


# Example usage
# file_processor = FileAudioProcessor("path/to/your/audiofile.mp3")

# while True:
#     chunk = file_processor.read_chunk()
#     if chunk is None:
#         break
    # Process the chunk

# No need to close the file as pydub handles it internally
