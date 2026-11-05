import os
import pandas as pd
from pydub import AudioSegment

def build_custom_dataset(raw_folder="raw_m4a", output_folder="custom_speech_dataset/audio_clips", csv_path="custom_speech_dataset/metadata.csv", keyword="audio"):
    # 1. Ensure output directories exist
    os.makedirs(output_folder, exist_ok=True)
    
    if not os.path.exists(raw_folder):
        print(f"Error: The input folder '{raw_folder}' does not exist. Please place your .m4a files there.")
        return

    # 2. Find all raw .m4a files
    files = [f for f in os.listdir(raw_folder) if f.lower().endswith('.m4a')]
    files.sort() # Keeps them in order
    
    if not files:
        print(f"No .m4a files found in '{raw_folder}/'.")
        return

    print(f"Found {len(files)} raw audio files. Processing...")

    metadata_records = []

    # 3. Convert, rename, and log to metadata
    for index, filename in enumerate(files, start=1):
        input_path = os.path.join(raw_folder, filename)
        
        # Define clean sequential name
        new_filename = f"{keyword}_{index}.wav"
        output_path = os.path.join(output_folder, new_filename)
        
        try:
            # Convert .m4a to 16kHz Mono .wav using FFmpeg under the hood
            audio = AudioSegment.from_file(input_path, format="m4a")
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(output_path, format="wav")
            
            # Add record for metadata.csv (transcript is the keyword you spoke)
            metadata_records.append({
                "filename": new_filename,
                "transcript": keyword
            })
            
            print(f"Processed: {filename} -> {new_filename}")
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

    # 4. Automatically save the metadata.csv file
    df = pd.DataFrame(metadata_records)
    df.to_csv(csv_path, index=False)
    
    print(f"\nSuccess! Dataset created:")
    print(f"- Audio clips saved in: '{output_folder}/'")
    print(f"- Metadata file saved at: '{csv_path}'")

if __name__ == "__main__":
    build_custom_dataset()