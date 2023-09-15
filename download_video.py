import sys
from sd_lib import download_mp4

#
# To do: Automatically download video from Twitter or Telegram if implied by URL 
#

def main(url=None, filename=None):
    # Ask user for the URL if unspecified
    if url is None:
        url = input("Please enter the URL of the MP4 file: ")
    if filename is None:
        filename = 'video.mp4'
        
    # Download mp4 file
    if download_mp4(url, filename):
        print('File downloaded successfully as ' + filename )
    
if __name__ == "__main__":    
    # Extract arguments from terminal
    url      = sys.argv[1] if len(sys.argv) > 1 else None
    filename = sys.argv[2] if len(sys.argv) > 2 else None
    
    main(url, filename)
