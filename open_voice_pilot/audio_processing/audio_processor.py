from abc import ABC, abstractmethod
import wave
import pyaudio
from pydub import AudioSegment

# Abstract Class
class AudioProcessor(ABC):
    @abstractmethod
    def read_chunk(self):
        pass

    @abstractmethod
    def close(self):
        pass

# File Audio Processor
from pydub import AudioSegment
from pydub.utils import make_chunks

class FileAudioProcessor:
    def __init__(self, filepath, chunk_size=1024):
        # pydub calculates in milliseconds
        self.chunk_size_ms = chunk_size * 1000 // 44100 
        self.audio = AudioSegment.from_file(filepath)
        self.chunks = make_chunks(self.audio, self.chunk_size_ms)
        self.current_chunk = 0

    def read_chunk(self):
        if self.current_chunk < len(self.chunks):
            chunk_data = self.chunks[self.current_chunk].raw_data
            self.current_chunk += 1
            return chunk_data
        else:
            return None
    
    def close(self):
        """
        No need to close the file as pydub handles it internally
        """
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
        return self.stream.read(self.chunk_size)

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