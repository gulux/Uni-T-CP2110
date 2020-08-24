# Uni-T-CP2110
Read data from Uni-T multimeter UT171A with CP2110 USB-to-UART bridge under linux

There is a base class UTHID which can be derived for other DMMs.

Download and install required Python and OS libs.

To work with UT171A run on command line:
    python3 -m ut-cp2110.UT171A

Testing:
    python3 -m ut-cp2110.testing.UTTest
    
More information on my homepage [smartypies.com/projects/ut171a-data-reader-on-linux/](http://smartypies.com/projects/ut171a-data-reader-on-linux/)
