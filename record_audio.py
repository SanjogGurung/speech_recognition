import os
import wave
import pyaudio
import pandas as pd

def record_audio(output_folder="custom_speech_dataset/audio_clips", keyword="audio", record_seconds=3):
    """
    Records audio directly from the microphone and saves it as a .wav file.
    Note: Even though your folder is named raw_m4a, this script records 
    uncompressed .wav files directly which python can process easily.
    """
    os.makedirs(output_folder, exist_ok=True)
    
    # Determine the next file number automatically
    existing_files = [f for f in os.listdir(output_folder) if f.lower().endswith(('.wav'))]
    next_index = len(existing_files) + 1
    filename = f"audio_{next_index}.wav"
    output_path = os.path.join(output_folder, filename)

    metadata_records = []

    # Add record for metadata.csv (transcript is the keyword you spoke)
    metadata_records.append({
        "filename": filename,
        "transcript": keyword
    })


    

    # Audio parameters
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    p = pyaudio.PyAudio()

    print(f"Preparing to record... Speak your command ('{keyword}') with your delayed pacing.")
    input("Press Enter to START recording...")

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* Recording live... Press Enter again when you are done speaking.")

    frames = []
    
    import threading
    is_recording = True

    def wait_for_stop():
        nonlocal is_recording
        input()
        is_recording = False

    stop_thread = threading.Thread(target=wait_for_stop)
    stop_thread.start()

    try:
        while is_recording:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
    except Exception as e:
        print(f"Recording stopped due to error: {e}")

    print("* Finished recording.")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded audio data into a .wav file
    wf = wave.open(output_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"Success! Audio saved to: {output_path}")

    df = pd.DataFrame(metadata_records)

    metadata_path = "custom_speech_dataset/metadata.csv"

    # Append if metadata.csv already has rows; rewrite whole file so blank lines are dropped
    if os.path.exists(metadata_path) and os.path.getsize(metadata_path) > 0:
        existing = pd.read_csv(metadata_path)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_csv(metadata_path, index=False, lineterminator="\n")

    print(f"Metadata saved to: {metadata_path}")




if __name__ == "__main__":

    keyboard = input("Please enter the keyword you want to record: ")
    record_audio(keyword=keyboard)

