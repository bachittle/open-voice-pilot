import sys
import ffmpeg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

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

# Initialize plot
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)

# Function to update the audio waveform
def update_waveform(frame, audio_data, sample_rate):
    """Update the waveform for animation."""
    max_points = frame * sample_rate // 10  # Points to display per frame
    if max_points > len(audio_data):
        max_points = len(audio_data)
    ax.set_xlim(0, max_points)
    line.set_data(np.arange(max_points), audio_data[:max_points])
    
    # Force redraw of the entire figure
    fig.canvas.draw()
    
    return line,

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <mp3_file_path>")
        sys.exit(1)

    mp3_file_path = sys.argv[1]
    audio_data, sample_rate, channels = load_audio(mp3_file_path)

    # Setting initial limits for the x-axis and y-axis
    ax.set_ylim(np.min(audio_data), np.max(audio_data))

    # Creating the animation
    anim = FuncAnimation(fig, update_waveform, fargs=(audio_data, sample_rate),
                         frames=range(1, 1000), interval=0, blit=False)

    plt.show()
