add:
drone crash
buck converter
capacitor test

For my initial set up to test the V36SE12005NRFA buck converter I connected a 5000 mAh battery with alligator clips to the baord. I used a multimeter to read the output voltage. The goal of the test was to see whether the buck converter reduced the voltage to 12v. 
![Buck converter diagram](image-5.png)  
I connected the positive lead of the battery to +Vin and the negative lead to -Vin
![Buck converter and batter](IMG_2957-1.jpg)


As a result a part of the buck conveter sparked and popped. It left visible damage on the converter.  

![alt text](IMG_2956.jpg)  

For the second set up I looked at the datasheet for the buck converter and followed the provided wiring diagram.
![alt text](image-10.png)  
I connected the sense + and sense - pins to Vo+ and Vo- respectivly. I also connected the on/off pin to the -vin pin.

![alt text](image-9.png)