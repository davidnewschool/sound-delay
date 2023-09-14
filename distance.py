def compute_speed_of_sound(temperature):
    # Speed of sound in air depending on temperature (meters/second)
    return 331 + 0.6*temperature

def compute_distance_and_error(flash_time, boom_time, speed_of_sound, frame_rate):
    # Compute distance and error estimate
    distance = (boom_time - flash_time) * speed_of_sound
    error = (0.5/frame_rate) * speed_of_sound
    return distance, error

def display_results(flash_time, boom_time, speed_of_sound, temperature, distance, error):
    # Output to terminal
    print(f'( {boom_time:.2f} - {flash_time:.2f} ) [s] * {speed_of_sound:.0f} [m/s] @ {temperature:.0f} [deg C]')
    print(f'  = {distance:.0f} +/- {error:.0f} meters')

def get_missing_inputs(flash_time, boom_time, temperature):
    """Prompt the user for any missing inputs."""
    if flash_time is None:
        flash_time = float(input('Enter time of flash: '))
    if boom_time is None:
        boom_time = float(input('Enter time of boom: '))
    if temperature is None:
        temperature = float(input('Enter local temperature in degrees C: '))
    return flash_time, boom_time, temperature

def main(flash_time=None, boom_time=None, temperature=None, frame_rate=25.0):
    # Get any missing inputs
    flash_time, boom_time, temperature = get_missing_inputs(flash_time, boom_time, temperature)
    
    speed_of_sound = compute_speed_of_sound(temperature)
    distance, error = compute_distance_and_error(flash_time, boom_time, speed_of_sound, frame_rate)
    display_results(flash_time, boom_time, speed_of_sound, temperature, distance, error)

if __name__ == "__main__":
    import sys

    # Extract arguments from terminal
    flash_time = float(sys.argv[1]) if len(sys.argv) > 1 else None
    boom_time = float(sys.argv[2]) if len(sys.argv) > 2 else None
    temperature = float(sys.argv[3]) if len(sys.argv) > 3 else None
    frame_rate = float(sys.argv[4]) if len(sys.argv) > 4 else 25.0
    
    main(flash_time, boom_time, temperature, frame_rate)