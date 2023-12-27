# Fusion-360-Camera-Control
This is a repo containing a collection of Fusion360 scripts and Add-Ins that allow for control of the Camera. 

## Controller_Input_v2
This is an Add-In instead of a script. It is designed to work with the os3m mouse. 

## Rotate_test_v3
This is the first functional version that can take in gamepad controls using pygame and manipulate the camera in fusion 360. 

To get it working you will have to setup your own `settings.json` and `.env`. I recommend making a script and copying the variables generated to make your versions. 

To get it working `rotate_test_v3` should be added as a script to Fusion 360. 

Because I haven't gotten threading working yet, so there is no concept of starting or stopping the script, it is limited to running for 30 seconds. 