# Motion Capture Room

## Set Up
The first thing you must do to set up the motion capture room is turn on the system, plug in the enthernet cable, and plug in the hardware key. Once you have completed those things you can open motive.
![Mocap setup step 1](Images/mocap_setup1.jpg) 
When you start up motive, you will be given some options to choose from. If you have not performed a calibration before you should press "perform camera calibration". 
![Mocap setup step 1.5](Images/calibration1.png) 
You will be brought to this screen. you must click on the "start wanding" button near the top right.
![Mocap setup step 1.5](Images/calibration2.png) 
Once you clock start wanding take the wand out and assemble it. It should look like this once assembled.
![Mocap setup step 2](Images/mocap_setup2.jpg)
When you first start motive the cameras should look blue. This will change when you start a calibration. All the cameras should appear as if they were turned off. Here they appear slightly pink due to the camera. In person they will appear grey.
![Mocap setup step 3](Images/mocap_setup3.jpg)
![Mocap setup step 4](Images/mocap_setup4.jpg)
Now you must take the wand and stand in front of a camera. Hold the wand so the motion capture markers are pointed straight up. You need to rotate your arm so the wand makes a circle in fron of the camera. You will be able to see the camera turn green depending on where you point the wand. Carefully trace out a circle until the whole camera appears green.  
![Mocap setup step 5](Images/mocap_setup5.jpg)  
![Mocap setup step 6](Images/mocap_setup6.jpg)     
Once you have done that for every camera you can go back to your computer. It should look soemthing like this:  
![Mocap setup step 1.5](Images/calibration3.png)   
Press the calculate button and wait for it to finish. A window should pop up with a calibration result. If it says exceptional you can click apply. If it says poor, you should retry the calibration.  
![Mocap setup step 1.5](Images/calibration4.png)  
After calibrating the cameras the last step is to set the origin. There is a small tape x in the center of the room. Take the origin and place it with z facing the operators table and x facing towards the wall. Once you have done that go to your computer and press "set plane". You can remove the origin afterwards.  
![Mocap setup step 7](Images/mocap_setup7.jpg)
## Data Collection
You can collect data of a single or multiple rigid bodies using the motion capture room. Place at least 3 markers on the rigid body you want to track. The markers must not be placed in areas where they may move relative to eachother. They should also be placed asymmetrically. 
![data collection step 7](Images/crazyflie_with_markers.jpg)
![data collection step 1](Images/data_collection1.png)
![data collection step 2](Images/data_collection2.png)
![data collection step 3](Images/data_collection3.png)
![data collection step 4](Images/data_collection4.png)
![data collection step 5](Images/data_collection5.png)
![data collection step 6](Images/data_collection6.png)
![data collection step 7](Images/data_collection7.png)
## Plotting