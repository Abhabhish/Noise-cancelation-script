import os
import subprocess
import uuid
from audoai.noise_removal import NoiseRemovalClient
import concurrent.futures

def extract_audio_from_video(input_video, unique_name):
    output_audio = f'noisy_audio_{unique_name}.mp3'
    cmd = [
        'ffmpeg',
        '-i', input_video,
        '-vn',
        '-acodec', 'libmp3lame',
        '-q:a', '0',
        output_audio
    ]
    subprocess.run(cmd, check=True)
    print('Audio Separation Done!')
    return output_audio

def clean_audio(noisy_audio, api_key, unique_name):
    noise_removal = NoiseRemovalClient(api_key=api_key)
    noise_removal_result = noise_removal.process(noisy_audio)
    cleaned_audio = f'denoised_audio_{unique_name}.mp3'
    noise_removal_result.save(cleaned_audio)
    print('Audio Cleaned')
    return cleaned_audio

def paste_audio_into_video(input_video, output_video, denoised_audio):
    cmd = [
        'ffmpeg',
        '-i', input_video,
        '-i', denoised_audio,
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_video
    ]
    subprocess.run(cmd, check=True)
    print('Audio added with FFmpeg without re-encoding the video.')

def process_video(input_video, output_video):
    try:
        unique_name = str(uuid.uuid4())
        noisy_audio = extract_audio_from_video(input_video, unique_name)
        api_key = '452fa4b2d4f7c0736549abd4b61140ff'
        denoised_audio = clean_audio(noisy_audio, api_key, unique_name)
        paste_audio_into_video(input_video, output_video, denoised_audio)
        os.remove(noisy_audio)
        os.remove(denoised_audio)
        print("Audio cleaning and video editing completed successfully!")
    except:
        pass

def main():
    src = input('src: ')
    dest = input('dest: ')

    all_tasks = []
    for root, dirs, files in os.walk(src):
        dest_root = root.replace(src, dest)
        if not os.path.exists(dest_root):
            os.makedirs(dest_root)
        for file in files:
            input_path = os.path.join(root, file)
            output_path = os.path.join(dest_root, file)
            all_tasks.append((input_path, output_path))

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_video, task[0], task[1]) for task in all_tasks]
        for future in concurrent.futures.as_completed(futures):
            future.result()  # This will raise any exceptions caught during the execution of the thread

if __name__ == '__main__':
    main()
