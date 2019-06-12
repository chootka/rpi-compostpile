#!/usr/bin/env python

#
# Script for Raspberry Pi for sending image data to one half of an arduino radio pair
# and receiving image data back from the other half of that pair.
#

from __future__ import print_function
import time
from RF24 import *
import RPi.GPIO as GPIO

########### USER CONFIGURATION ###########
# Setup for GPIO 15 CE and CE0 CSN for RPi B+ with SPI Speed @ 8Mhz
radio = RF24(RPI_BPLUS_GPIO_J8_15, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ)

##########################################
def try_read_data(channel=0):
    if radio.available():
        while radio.available():
            len = radio.getDynamicPayloadSize()
            receive_payload = radio.read(len)
            print('Got payload size={} value="{}"'.format(len, receive_payload.decode('utf-8')))
            # First, stop listening so we can talk
            radio.stopListening()

            # Send the final one back.
            radio.write(receive_payload)
            print('Sent response.')

            # Now, resume listening so we catch the next packets.
            radio.startListening()

status = 0
pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]
payload_size = 32
payload_index = 0
max_payload_size = 64
send_payload = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ789012abcdefghijklmnopqrstuvwxyz3456!?'
millis = lambda: int(round(time.time() * 1000))

radio.begin()
radio.enableDynamicPayloads()
radio.setRetries(5, 15)
radio.printDetails()

print('Role: Ping Out, starting transmission')
radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])

# forever loop
while 1:

    if status == 0:
        # The payload will always be the same, what will change is how much of it we send.

        # First, stop listening so we can talk.
        radio.stopListening()

        # Take the time, and send it.  This will block until complete
        print('Now sending length={} index={} end={} ... '.format(payload_size, payload_index, payload_index+payload_size), end="")
        radio.write(send_payload[payload_index:payload_index+payload_size])

        # Now, continue listening
        # radio.startListening()

        # # Wait here until we get a response, or timeout
        # started_waiting_at = millis()
        # timeout = False
        # while (not radio.available()) and (not timeout):
        #     if (millis() - started_waiting_at) > 500:
        #         timeout = True

        # # Describe the results
        # if timeout:
        #     print('failed, response timed out.')
        # else:
        #     try_read_data()

        # # Increment payload index to next chunk for next time
        payload_index += payload_size
        if payload_index >= max_payload_size:
            print('EOF')
            status = 1

    else:
        print('Finished sending file')
        payload_index = 0
        status = 0

    time.sleep(0.1)
