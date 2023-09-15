import sys
from sd_lib import compute_distance

def main(flash_time, boom_time, temperature, frame_rate):
    # Get missing inputs
    if flash_time is None:
        flash_time = float(input('Enter time of flash: '))
    if boom_time is None:
        boom_time = float(input('Enter time of boom: '))
    if temperature is None:
        temperature = float(input('Enter local temperature in degrees C: '))

    # Compute distance and error
    distance, error, speed_of_sound = compute_distance(flash_time, boom_time, temperature, frame_rate)
    
    # Display results to terminal
    print(f'( {boom_time:.2f} - {flash_time:.2f} ) [s] * {speed_of_sound:.0f} [m/s] @ {temperature:.0f} [deg C]')
    print(f'  = {distance:.0f} +/- {error:.0f} meters')

if __name__ == "__main__":
    
    # Extract arguments from terminal
    flash_time  = float(sys.argv[1]) if len(sys.argv) > 1 else None
    boom_time   = float(sys.argv[2]) if len(sys.argv) > 2 else None
    temperature = float(sys.argv[3]) if len(sys.argv) > 3 else None
    frame_rate  = float(sys.argv[4]) if len(sys.argv) > 4 else None
    
    main(flash_time, boom_time, temperature, frame_rate)
