# Boards


Non adjustable-

[Polulu D42V55F18](https://www.pololu.com/product/5578)

[Delta Electronics V36SE12005NRFA](https://www.mouser.com/ProductDetail/Delta-Electronics/V36SE12005NRFA?qs=sGAEpiMZZMsc0tfZmXiUnQ%252BwKZhbvwnuOeKk3OAcehuIStk1xIzkow%3D%3D)

Adjustable-

[Core Electronics](https://core-electronics.com.au/dc-dc-adjustable-step-down-module-5a-75w.html)


https://www.ufinebattery.com/blog/lipo-battery-discharge-rate-guide-calculation-tips/
https://www.ufinebattery.com/blog/4s-lipo-battery-voltage-chart-full-nominal-storage-and-cutoff-explained/




We will be using a buck converter in order to safely power the Jetson Orin Nx that will be onboard the 10-inch drone. The battery will serve as the input for the converter, and the output voltage will go to the board. The voltage range of the LiPo battery we are using is 19.8V-25.2V, and the NX module is rated for 5V-20V. The converter must bring down the input voltage and deliver a voltage within the range of the NX module. 

The Polulu D42v55f18 buck converter is a small voltage regulator, around 1” x 1” in size. It has an input voltage range of 18V-60V and a maximum output current of 4 Amps. The converter is rated to output a steady 18V, which is within the range for the NX module.

I first soldered wires onto the board following the pin markings on the board. I connected the board to a breadboard in order to test it. A bench power supply was used for controlled tests of the converter. 

Initially, I set the bench power supply to output 20V at .2 Amps. Once I confirmed the converter was working properly, I began to test it at different voltages. From what I could find, a lipo battery’s minimum safe voltage is 3.3V per cell. Since it is a 6s (6-cell) battery, the minimum should be 19.8V. However, from previous testing, I found that the drone does not fly below 21.6V or 3.6V per cell. I decided to test both as well as the nominal voltage of 3.7V per cell, and the maximum voltage of 4.2V per cell. Thus, the converter was tested at 19.8V, 21.6V, 22.2V, and 25.2V. This same test was repeated for 2 and 3 Amps as well.



19.8v at .2 amps  18.01v

21.6v at .2 amps  18.01v

22.2v at .2 amps  18.01v

25.2v at .2 amps  18.02v


19.8v at 2 amps  18.01v

21.6v at 2 amps  18.01v

22.2v at 2 amps  18.01v

25.2v at 2 amps  18.02v


19.8v at 3 amps  18.01v

21.6v at 3 amps  18.01v

22.2v at 3 amps  18.02v

25.2v at 3 amps  18.02v




