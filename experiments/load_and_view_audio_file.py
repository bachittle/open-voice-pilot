import sys
import ffmpeg
import numpy as np
import matplotlib.pyplot as plt
import simpleaudio as sa

def load_audio(file_path):
    """Load audio data from an MP3 file using FFmpeg and get the sample rate and number of channels."""
    try:
        probe = ffmpeg.probe(file_path)
        sample_rate = int(probe['streams'][0]['sample_rate'])
        channels = int(probe['streams'][0]['channels'])

        out, _ = (
            ffmpeg
            .input(file_path)
            .output('pipe:', format='wav')
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        return np.frombuffer(out, np.int16), sample_rate, channels
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        sys.exit(1)

def plot_audio_waveform(audio_data):
    """Plot the audio waveform using Matplotlib."""
    plt.figure(figsize=(10, 4))
    plt.plot(audio_data)
    plt.title("Audio Waveform")
    plt.xlabel("Samples")
    plt.ylabel("Amplitude")
    plt.show()

def play_audio(audio_data, sample_rate, channels):
    """Play audio from a numpy array."""
    # Convert numpy array to audio buffer
    audio_buffer = audio_data.tobytes()
    # Play audio
    play_obj = sa.play_buffer(audio_buffer, channels, 2, sample_rate)
    play_obj.wait_done()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <mp3_file_path>")
        sys.exit(1)

    mp3_file_path = sys.argv[1]
    audio_data, sample_rate, channels = load_audio(mp3_file_path)
    print(f"sample rate: {sample_rate}, channels: {channels}")
    plot_audio_waveform(audio_data)
    play_audio(audio_data, sample_rate, channels)
