import os
import numpy as np
import matplotlib.pyplot as plt
from mosqito.utils import load
from mosqito.sq_metrics import loudness_zwtv
import cv2
import plotly.graph_objects as go
import requests
from IPython.display import display, HTML

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

def download_mp4(url, filename=None):
    """Download mp4 file from URL"""

    # Default filename to 'video.mp4'
    if filename is None:
        filename = 'video.mp4'
    
    # Send HTTP request for file
    try:
        response = requests.get(url)
        if response.status_code == 200:
            filename = 'video.mp4'
        else:
            print(f"Request failed with status code {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
        
    # Write file to disk
    with open(filename, 'wb') as f:
        f.write(response.content)

    return True

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
    return red_intensity, time_video, frame_rate

def get_axis_limits(time_video, loudness, red_intensity):
    # Get axis limits
    time_min = time_video[0]
    time_max = time_video[-1]

    # Pad top and bottom of figure with 10% of range of signals
    red_min = np.min(red_intensity) - 0.1*( np.max(red_intensity) - np.min(red_intensity) )
    red_max = np.max(red_intensity) + 0.1*( np.max(red_intensity) - np.min(red_intensity) )

    # Set loudness axis so that the max and min appear the same as red intensity
    loud_min = np.min(loudness) - ( np.max(loudness) - np.min(loudness) ) \
                                  * ( np.min(red_intensity) - red_min ) \
                                  /( np.max(red_intensity) - np.min(red_intensity) )
    loud_max = np.max(loudness) + ( np.max(loudness) - np.min(loudness) ) \
                                  * ( red_max - np.max(red_intensity) ) \
                                  /( np.max(red_intensity) - np.min(red_intensity) )

    return time_min, time_max, red_min, red_max, loud_min, loud_max
    
def plot_signals_matplotlib(loudness, time_audio, red_intensity, time_video, video_path):
    """Plot the audio and video signals with Matplotlib."""

    # Get limits of plot axes
    time_min, time_max, red_min, red_max, loud_min, loud_max = get_axis_limits(loudness, red_intensity)
    
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

def plot_signals_plotly(loudness, time_audio, red_intensity, time_video, video_path, frame_rate):
    """Plot the audio and video signals with Plotly."""
    
    # Get limits of plot axes
    time_min, time_max, red_min, red_max, loud_min, loud_max = get_axis_limits(loudness, red_intensity)
    
    # Create a figure
    fig = go.Figure()

    # Add Loudness and Red Intensity traces
    fig.add_trace(go.Scatter(x=time_audio, y=loudness, mode='lines', line=dict(color='blue'), yaxis='y2'))
    fig.add_trace(go.Scatter(x=time_video, y=red_intensity, mode='lines', line=dict(color='red')))

    # Update the layout
    fig.update_layout(
        xaxis      = dict(title       = "Time [seconds]",
                          range       = [time_min, time_max],
                          rangeslider = dict(visible=True),
                          type        = 'linear'),
        yaxis  = dict(title           = "Mean Red Intensity [0-255]",
                          side        = 'left',
                          tickfont    = dict(color='red'),
                          titlefont   = dict(color='red'),
                          showgrid    = False,
                          range       = [red_min, red_max]),
        yaxis2 = dict(title           = "Loudness [sones]",
                          overlaying  = 'y', 
                          side        = 'right',
                          tickfont    = dict(color='blue'),
                          titlefont   = dict(color='blue'),
                          showgrid    = False,
                           range       = [loud_min, loud_max]),
        showlegend = False,
        title      = "Comparison of Loudness and Red Intensity over Time"
    )

    # Update the layout
    fig.update_layout(
        xaxis = dict(ticklen  = 10,   # Length of major ticks
                     showgrid = True, # Gridlines
        )
    )

    # Calculate total duration in seconds (round up)
    total_seconds = int(np.ceil(time_audio[-1]))

    # Update x-axis for minor ticks representing each frame within a second when zoomed in
    fig.update_xaxes(
        minor_tickmode = "linear",
        minor_tick0    = 0,
        minor_dtick    = 1./frame_rate,
        minor_ticklen  = 0,  # Length of minor ticks
        minor_showgrid = True,
        minor_nticks   = int(frame_rate * total_seconds)  # Maximum number of minor ticks
    )

    # Display the plot
    fig.show()

def compute_distance(flash_time, boom_time, temperature, frame_rate):
    """Compute distance from sound delay"""

    # Set input defaults
    if temperature is None:
        temperature = 20.
    if frame_rate is None:
        frame_rate = 25.

    # Compute speed of sound
    speed_of_sound = 331. + 0.6*temperature

    # Compute distance estimate and error bounds
    distance = ( boom_time - flash_time )*speed_of_sound
    error    = (0.5/frame_rate)*speed_of_sound
    
    return distance, error, speed_of_sound    
