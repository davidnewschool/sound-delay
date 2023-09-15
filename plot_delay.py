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

#For using the variables global
loudness = None
time_audio = None
red_intensity = None
time_video = None
frame_rate = None
audio_path = None

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

    time_video = (1./frame_rate) * np.linspace(0., nframes, nframes, endpoint=False)
    return red_intensity, time_video

def plot_signals(loudness, time_audio, red_intensity, time_video, video_path):
    """Plot the audio and video signals."""
    
    # Get axis limits
    time_min = time_video[0]
    time_max = time_video[-1]

    red_min = np.min(red_intensity) - 0.1*( np.max(red_intensity) - np.min(red_intensity) )
    red_max = np.max(red_intensity) + 0.1*( np.max(red_intensity) - np.min(red_intensity) )

    loud_min = np.min(loudness) - ( np.max(loudness) - np.min(loudness) ) \
                                  * ( np.min(red_intensity) - red_min ) \
                                  /( np.max(red_intensity) - np.min(red_intensity) )
    loud_max = np.max(loudness) + ( np.max(loudness) - np.min(loudness) ) \
                                  * ( red_max - np.max(red_intensity) ) \
                                  /( np.max(red_intensity) - np.min(red_intensity) )

    # Plot
    fig = plt.figure()
    ax1 = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax2 = ax1.twiny()
    ax3 = ax1.twinx()
    ax1.plot(time_video, red_intensity, 'r-')
    ax2.plot(np.arange(len(time_video))+1., red_intensity, 'r-')
    ax3.plot(time_audio, loudness, 'b-')

    # Time-Red intensity axis
    ax1.set_xlim(time_min, time_max)
    ax1.set_ylim(red_min, red_max)
    ax1.tick_params(axis='y', colors='red')
    ax1.set_xlabel('Time [seconds]')
    ax1.set_ylabel('Mean Red Intensity [0-255]', color='red')

    # Frame-Red intensity axis
    ax2.set_xlim(1., float(len(time_video)))
    ax2.set_ylim(red_min, red_max)
    ax2.set_xlabel('Video Frame #')
    ax2.xaxis.grid(linestyle='--')
    
    # Loudness axis
    ax3.set_ylim(loud_min, loud_max)
    ax3.tick_params(axis='y', colors='blue')
    ax3.set_ylabel('Loudness [sones]', color='blue')
    
    # Save the plot to the same path/name as the input video
    output_image_path = os.path.splitext(video_path)[0] + '.png'
    plt.savefig(output_image_path)

    # Show the plot
    plt.show()

def main(video_path=None, audio_path=None):
    global loudness, time_audio, red_intensity, time_video
    
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
