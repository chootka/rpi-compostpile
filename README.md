# rpi-compostpile  
**Steps to set up the Raspberry Pi to communicate via the NRF24L01+ radio**  
0/ flash SD card with latest raspbian stretch lite (from April 19)   

1/ Be sure to include an empty file named `ssh` in the root of your newly flashed SD card so you can SSH into it later  

2/ Connect to your pi with user `pi` and default password `raspberry`  
`$ ssh pi@raspberrypi.local`  
  
3/ Go into the raspi-config tool and change the default password!!! Additionally, enable SPI, expand system to take up the full disk space of your SD card and join a wireless network so you are connected to the internet.  
`$ sudo raspi-config`  

4/ Install git, RF24 for radio comms and other image processing libraries  
`$ sudo apt-get update`  
`$ sudo apt-get install git libboost-python-dev python-pip libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev pillow python-requests -y`  
`$ git clone https://github.com/nRF24/RF24.git`  
`$ cd RF24`  
`$ sudo make install`  
`$ cd pyRF24`  
`$ sudo python setup.py build`  
`$ sudo python setup.py install`  

5/ Install this repo  
`$ git clone https://github.com/chootka/rpi-compostpile.git`  
`$ cd rpi-compostpile`  

6/ Add the script to your profile so it boots automatically on start up
`$ sudo nano /etc/profile`  
`$ sudo python /home/pi/p2p/parent-children.py &`

7/ Reboot
