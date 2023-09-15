import sys 
from sd_lib import get_video_path, get_audio_path, process_audio, process_video, plot_signals

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
