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


# Microphone Audio Processor
class MicrophoneAudioProcessor(AudioProcessor):
    def __init__(self, chunk_size=1024, format=pyaudio.paInt16, channels=1, rate=44100):
        self.chunk_size = chunk_size
        self.format = format
        self.channels = channels
        self.rate = rate
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk_size)

    def read_chunk(self):
        # Implementation to read a chunk of data from the microphone
        data = self.stream.read(self.chunk_size)
        # Convert raw data to numpy array
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