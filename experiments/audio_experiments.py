import open_voice_pilot.audio_processing as ap 
import time
import argparse
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

def print_chunks(processor):
    i = 0
    start_time = time.time()
    while True:
        chunk = processor.read_chunk()
        if not chunk:
            break
        elapsed_time = time.time() - start_time
        avg_time_per_chunk = (elapsed_time / i) * 1000 if i != 0 else 0
        print(f"\rChunk {i}: {len(chunk)}, Elapsed time: {elapsed_time:.2f} s, average time per chunk: {avg_time_per_chunk:.2f} ms.  ", end="")
        i += 1

audio_data_buffer = []

def visualize_chunks(processor):
    # Initialize plot
    fig, ax = plt.subplots()
    line, = ax.plot([], [], lw=2)

    def update_waveform(frame, audio_data, sample_rate):
        global audio_data_buffer
        chunk = processor.read_chunk()
        if not chunk.any():
            return line,
        audio_data_buffer = np.append(audio_data_buffer, chunk)
        audio_data = audio_data_buffer
        max_points = frame * sample_rate // 10
        if max_points > len(audio_data):
            max_points = len(audio_data)
        ax.set_xlim(0, max_points)
        line.set_data(np.arange(max_points), audio_data[:max_points])
        fig.canvas.draw()
        return line,

    sample_rate = 44100
    audio_data = []
    ax.set_ylim(-2**15, 2**15 - 1)
    anim = FuncAnimation(fig, update_waveform, fargs=(audio_data, sample_rate),
                         frames=range(1, 1000), interval=0, blit=False)
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Run audio processing experiments with Open Voice Pilot tools.")
    parser.add_argument('--mode', choices=['file', 'mic'], required=True, help="Select mode: 'file' for audio file processing, 'mic' for microphone input.")
    parser.add_argument('--file', help="Path to the audio file for 'file' mode.")
    parser.add_argument('--output', choices=['print', 'visualize'], default='print', help="Select output: 'print' to print chunks, 'visualize' to visualize chunks.")
    
    args = parser.parse_args()

    if args.mode == 'file':
        if not args.file:
            print("Audio file path is required for 'file' mode.")
            return
        processor = ap.FileAudioProcessor(args.file)
    elif args.mode == 'mic':
        mic_index = ap.select_microphone()  # Select microphone interactively
        processor = ap.MicrophoneAudioProcessor(device_index=mic_index)  # Initialize processor with selected microphone

    if args.output == 'print':
        print_chunks(processor)
    elif args.output == 'visualize':
        visualize_chunks(processor)

    processor.close()

if __name__ == "__main__":
    main()

