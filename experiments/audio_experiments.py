import open_voice_pilot.audio_processing as ap 
import time
import argparse

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

def main():
    parser = argparse.ArgumentParser(description="Run audio processing experiments with Open Voice Pilot tools.")
    parser.add_argument('--mode', choices=['file', 'mic'], required=True, help="Select mode: 'file' for audio file processing, 'mic' for microphone input.")
    parser.add_argument('--file', help="Path to the audio file for 'file' mode.")
    
    args = parser.parse_args()

    if args.mode == 'file':
        if not args.file:
            print("Audio file path is required for 'file' mode.")
            return
        processor = ap.FileAudioProcessor(args.file)
    elif args.mode == 'mic':
        processor = ap.MicrophoneAudioProcessor()

    print_chunks(processor)

if __name__ == "__main__":
    main()



