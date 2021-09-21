# rpi-compostpile  
**Steps to set up the Raspberry Pi to communicate via the NRF24L01+ radio**  
0/ flash SD card with latest raspbian stretch lite (from April 19)   

1/ Be sure to include an empty file named `ssh` in the root of your newly flashed SD card so you can SSH into it later  

2/ You will also want to enable SPI on by default (this is how the Rasbperry Pi will communicate with our radio) by editing the file called `config.txt` in the root of the Rasbperry Pi image and making sure that this is in there:  
`dtparam=spi=on`

2/ Connect to your pi with user `pi` and default password `raspberry`  
`$ ssh pi@raspberrypi.local`  
  
3/ Go into the raspi-config tool and change the default password!!! Additionally, enable SPI, expand system to take up the full disk space of your SD card and join a wireless network so you are connected to the internet.  
`$ sudo raspi-config`  

4/ Install git, RF24 for radio comms and other image processing libraries  
`$ sudo apt-get update`  
`$ sudo apt-get install git libboost-python-dev python-pip libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev python-pil python-requests -y`  
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

### Additional Resources ###  
Image to ASCII art converter: http://picascii.com/  
https://github.com/nRF24/RF24  
https://github.com/nRF24/RF24Network  
http://thezanshow.com/electronics-tutorials/raspberry-pi/tutorial-34-35  
http://spencernusbaum.com/wordpress/index.php/2018/07/22/working-with-the-nrf24l01-transcievers-on-the-raspberry-pi-and-arduino/  
https://howtomechatronics.com/tutorials/arduino/how-to-build-an-arduino-wireless-network-with-multiple-nrf24l01-modules/  
