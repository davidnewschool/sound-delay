import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from mosqito.utils import load
from mosqito.sq_metrics import loudness_zwtv
import cv2

try: 
    from moviepy.editor import VideoFileClip
except:
    pass  # If there's an error importing VideoFileClip, it will be handled later in the code.

def extract_audio_from_video(video_path):
    """Extract audio from the video."""
    try:
        # Ensure that VideoFileClip was successfully imported before proceeding.
        if 'VideoFileClip' not in globals():
            print("Warning: ffmpeg and moviepy must be installed to automatically extract audio.")
            return None

        # Construct the path for the audio file by replacing the video file extension with .wav.
        audio_path = os.path.splitext(video_path)[0] + '.wav'
        
        # Use moviepy to extract audio from the video and save it as a WAV file.
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_path, codec='pcm_s16le')
        audio.close()

        print("Audio extracted successfully!")
        return audio_path
    except Exception as e:
        print(f"Error encountered during audio extraction: {e}")
        return None

def get_video_path():
    """Prompt the user for the path to the video file and validate its existence."""
    while True:
        video_path = input('Enter path of video file: ')
        if os.path.exists(video_path) and os.path.isfile(video_path):
            print("Video found!")
            return video_path
        else:
            print("Video not found. Please check the path and try again.")

def get_audio_path(video_path=None):
    """ path for the audio."""
    audio_path = extract_audio_from_video(video_path)
    
    if audio_path:
        print("Will use the audio from the extraction of the video!")
        return audio_path
    
    print('You can still provide your own manually extracted audio file in .wav format.')
    while True:
        audio_path = input('Enter path of audio file: ')

        try:
            with open(audio_path, 'rb') as f:  # 'rb' mode is for reading binary files
                print("Audio found!")
                return audio_path  # Exit the loop once a valid audio path is provided
        except FileNotFoundError:
            print("Audio not found. Please check the path and try again.")

def process_audio(audio_path):
    """Load and compute loudness values for the given audio file."""
    print('Processing audio...')
    sig, fs = load(audio_path, wav_calib=2 * 2 **0.5)
    loudness, N_spec, bark_axis, time_audio = loudness_zwtv(sig, fs, field_type="free")
    return loudness, time_audio

def process_video(video_path):
    """Extract the red channel intensity over time from the given video file."""
    print('Processing video...')
    cap = cv2.VideoCapture(video_path)
    nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    red_intensity = np.zeros(nframes)

    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    print(str(frame_rate) + ' frames/second')

    frame_index = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        red_frame = frame[:, :, 2]
        red_intensity[frame_index] = red_frame.mean()
        frame_index += 1

    cap.release()
    cv2.destroyAllWindows()

    time_video = 0.04 * np.linspace(0., nframes, nframes, endpoint=False)
    return red_intensity, time_video

def plot_signals(loudness, time_audio, red_intensity, time_video, video_path):
    """Plot the audio and video signals."""
    # Rescale red intensity amplitude to match audio signal amplitude
    red_intensity = red_intensity - np.min(red_intensity) + np.min(loudness)
    red_intensity = red_intensity*np.max(loudness)/np.max(red_intensity)

    # Get min and max of time axis
    time_min = time_audio[0]
    time_max = time_audio[-1]

    # Get min and max of
    amp_min = np.min(red_intensity) - 0.1*( np.max(red_intensity) - np.min(red_intensity) )
    amp_max = np.max(red_intensity) + 0.1*( np.max(red_intensity) - np.min(red_intensity) )

    # Plot
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.plot(time_audio, loudness, 'b-')
    ax.plot(time_video, red_intensity, 'r-')
    ax.legend(['loudness','red intensity'])
    ax.set_xlim(time_min, time_max)
    ax.set_ylim(amp_min, amp_max)
    ax.set_yticks([])
    ax.set_xlabel('Time [seconds]')
    ax.set_ylabel('Amplitude')
    plt.grid()

    # Save the plot to the same path/name as the input video
    output_image_path = os.path.splitext(video_path)[0] + '.png'
    plt.savefig(output_image_path)

    # show the plot
    plt.show()

def main(video_path=None, audio_path=None):
    # If video_path is not given as argument, ask the user
    if not video_path:
        video_path = get_video_path()
    
    # If audio_path is not given as argument or extraction failed, ask the user
    if not audio_path:
        audio_path = get_audio_path(video_path)
    
    # Process audio and get loudness values
    loudness, time_audio = process_audio(audio_path)
    
    # Process video and get red intensity values
    red_intensity, time_video = process_video(video_path)
    
    # Plot the signals
    plot_signals(loudness, time_audio, red_intensity, time_video, video_path)

if __name__ == "__main__":
    # Assuming first argument is video_path and second is audio_path
    video_arg = sys.argv[1] if len(sys.argv) > 1 else None
    audio_arg = sys.argv[2] if len(sys.argv) > 2 else None
    
    main(video_arg, audio_arg)