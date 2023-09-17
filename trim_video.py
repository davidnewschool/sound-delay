import sys
import os
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
except:
    pass
    
def main(input_path=None, output_path=None):
    # Check for ffmpeg and moviepy
    if 'VideoFileClip' not in globals():
        print("Error: ffmpeg and moviepy must be installed")
        return None
    
    # Deal with missing input
    if input_path is None:
        # Ask the user for the path of the MP4 file
        input_path = input("Please enter the path of the video: ")
    if output_path is None:
        # Generate the output path with a "-cut" suffix
        foo = os.path.splitext(input_path)
        output_path = foo[0] + '-trimmed' + foo[1]
        
    # Load the video clip
    video_clip = VideoFileClip(input_path)

    # Give the user information about the duration of the clip
    video_duration = video_clip.duration
    print(f"The video duration is {video_duration:.2f} seconds.")

    # Define the start and end times for trimming (in seconds)
    start_time = float(input("Please enter the start time where you want to cut: "))  # Start time of the trimmed portion
    end_time = float(input("Please enter the end time where you want to cut: "))  # End time of the trimmed portion

    # Trim the video clip
    trimmed_clip = video_clip.subclip(start_time, end_time)

    # Save the trimmed video with audio
    trimmed_clip.write_videofile(output_path, codec="libx264")
    
    # Close the original video clip
    video_clip.close()

    print("Video trimming complete. Saved as " +  output_path)
    
if __name__ == "__main__":
    
    # Extract arguments from terminal
    input_path  = sys.argv[1] if len(sys.argv) > 1 else None
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    main(input_path, output_path)
