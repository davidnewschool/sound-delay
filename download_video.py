import sys
import requests

#
# To do: Automatically download video from Twitter or Telegram if implied by URL 
#

def main(url=None, filename=None):
    # Ask user for the URL if unspecified
    if url is None:
        url = input("Please enter the URL of the MP4 file: ")
    if filename is None:
        filename = 'video.mp4'

    # Send HTTP request for file
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Write file to disk
            with open(filename, 'wb') as f:
                f.write(response.content)
            print('File downloaded successfully as ' + filename )
        else:
            print(f"Request failed with status code {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
if __name__ == "__main__":    
    # Extract arguments from terminal
    url      = sys.argv[1] if len(sys.argv) > 1 else None
    filename = sys.argv[2] if len(sys.argv) > 2 else None
    
    main(url, filename)
