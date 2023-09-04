# Optional parameters
frame_rate = 25. # Video frame rate (frames/second)

# Get input parameters
flash_time  = float(input('Enter time of flash: '))
boom_time   = float(input('Enter time of boom: '))
temperature = float(input('Enter local temperature in degrees C: '))

# Speed of sound in air depending on temperature (meters/second)
speed_of_sound = 331 + 0.6*temperature

# Compute distance and error estimate
distance = ( boom_time - flash_time )*speed_of_sound
error    = ( 0.5/frame_rate )*speed_of_sound

# Output to terminal
print( '( ' + '{:.2f}'.format( boom_time ) + ' - ' + '{:.2f}'.format( flash_time ) + ' ) [s] * ' + '{:.0f}'.format( speed_of_sound ) + ' [m/s] @ ' + '{:.0f}'.format( temperature ) + ' [deg C]')
print( '  = ' + '{:.0f}'.format( distance ) + ' +/- '  + '{:.0f}'.format( error ) + ' meters')
