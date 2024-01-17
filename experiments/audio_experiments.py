import open_voice_pilot.audio_processing as ap 
import time
import argparse

def print_audio_file_chunks(audio_file_path):
    file_processor = ap.FileAudioProcessor(audio_file_path)
    i = 0
    start_time = time.time()
    while True:
        chunk = file_processor.read_chunk()
        if not chunk:
            break
        print(f"Chunk {i}: {len(chunk)}")
        i += 1
    
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time*1000:.2f} ms, average time per chunk: {(elapsed_time / i) * 1000:.2f} ms")

def print_microphone_chunks():
    mic_processor = ap.MicrophoneAudioProcessor()
    i = 0
    start_time = time.time()
    print("Press ctrl + c to stop the program\n")
    while True:
        chunk = mic_processor.read_chunk()
        elapsed_time = time.time() - start_time
        print(f"\rChunk {i}: {len(chunk)}, elapsed time: {elapsed_time:.2f} s, average time per chunk: {(elapsed_time / (i + 1)) * 1000:.2f} ms", end="")
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
        print_audio_file_chunks(args.file)
    elif args.mode == 'mic':
        print_microphone_chunks()

if __name__ == "__main__":
    main()
