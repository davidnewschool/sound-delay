import sys
import os
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    import moviepy.video.fx.all as vfx
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
        input_path = input("Enter the path of video: ")
    if output_path is None:
        # Generate the output path with a "-cut" suffix
        foo = os.path.splitext(input_path)
        output_path = foo[0] + '-cropped' + foo[1]
        
    # Load the video clip
    video_clip = VideoFileClip(input_path)
    
    # Get the dimensions of the video frame
    frame_width, frame_height = video_clip.size
    
    # Ask the user for the percentage to cut from each side
    top_percentage = float(input("Enter the percentage to cut from top (0-100): "))
    bottom_percentage = float(input("Enter the percentage to cut from bottom (0-100): "))
    left_percentage = float(input("Enter the percentage to cut from left (0-100): "))
    right_percentage = float(input("Enter the percentage to cut from right (0-100): "))

    # Calculate the pixel values to cut
    top_cut = int(frame_height * (top_percentage / 100))
    bottom_cut = int(frame_height * (bottom_percentage / 100))
    left_cut = int(frame_width * (left_percentage / 100))
    right_cut = int(frame_width * (right_percentage / 100))

    # Crop the video clip
    cropped_clip = video_clip.crop(y1=top_cut, y2=frame_height - bottom_cut, x1=left_cut, x2=frame_width - right_cut)

    # Write the edited video to the output file
    cropped_clip.write_videofile(output_path, codec="libx264")

    print("Video cropping complete. Saved as " +  output_path)
    
if __name__ == "__main__":
    
    # Extract arguments from terminal
    input_path  = sys.argv[1] if len(sys.argv) > 1 else None
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    main(input_path, output_path)
