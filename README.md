# Fusion-360-Game-Controller-Input
A Fusion 360 script that allows for gamepad / controller input to control the view / camera in Fusion 360

## Rotate_test_v3
This is the first functional version that can take in gamepad controls using pygame and manipulate the camera in fusion 360. 

To get it working you will have to setup your own `settings.json` and `.env`. I recommend making a script and copying the variables generated to make your versions. 

To get it working `rotate_test_v3` should be added as a script to Fusion 360. 

Because I haven't gotten threading working yet, so there is no concept of starting or stopping the script, it is limited to running for 30 seconds. 