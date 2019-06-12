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
def select_image(index=0):
    # Select an image from a folder
    # Break into byte array, set send_payload to equal this:
    # send_payload = [new image array]
    max_payload_size = len(send_payload)

def check_responses():
    # first check if the dictionary has entries for all children
    if len(received_payloads) < num_children:
        return False

    # then check if each child has the correct number of entries to its list
    for child in received_payloads:
        if len(received_payloads[child]) != transmission_id:
            return False

    return True

def read_ack(channel=0):
    if radio.available():
        while radio.available():
            len = radio.getDynamicPayloadSize()
            ack_payload = radio.read(len)
            print('Got payload size={} value={}\n'.format(len, ack_payload.decode('utf-8')))
            # First, stop listening so we can talk
            radio.stopListening()

            # Send the ack back
            radio.write(ack_payload)
            print('Sent ACK.\n')

            # Now, resume listening so we catch the next packets.
            radio.startListening()

def read_file_data(channel=0):
    if radio.available():
        while radio.available():
            len = radio.getDynamicPayloadSize()
            file_payload = radio.read(len)
            print('Got file data payload size={} value={}\n'.format(len, file_payload.decode('utf-8')))

            # Will need to know who sent this and save data per sender Arduino
            # key = file_payload.somehow get the header
            key = 'sender'
            if key in received_payloads:
                received_payloads[key].append(file_payload)
            else:
                received_payloads[key] = [file_payload]

	    print('Received payloads {}'.format(file_payload));
            # First, stop listening so we can talk
            radio.stopListening()

            # Send the final one back.
            # radio.write('ACK')
            # print('Sent ACK.\n')

            # Now, resume listening so we catch the next packets.
            radio.startListening()


##########################################
# MODES
#
# sending = 0 (when we select an image, transform to byte array and transmit to children)
# receiving = 1 (while we wait to hear back from children)
# saving = 2 (we heard back from all children, now save to DB)
# Then go back to 'init'!

status = 0
modes = ['sending', 'receiving', 'saving']

# Addressing
pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]

# How many transmissions for a file has been sent so far?
transmission_id = 1

# How many arduinos do we expect to hear from?
num_children = 1

# For now working with a fixed payload
send_payload = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ789012abcdefghijklmnopqrstuvwxyz3456!?'
max_payload_size = len(send_payload)
payload_index = 0
payload_size = 4

# Dict for saving received data from children arduinos
received_payloads = dict()

# Get the time
millis = lambda: int(round(time.time() * 1000))

radio.begin()
radio.enableDynamicPayloads()
radio.setRetries(5, 15)
radio.printDetails()

print('Current Status {}...\n'.format(modes[status]))
radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])

# forever loop
while 1:

    # sending data
    if status == 0:
        # Now send the first payload to the receiver Arduino. This will block until complete
        print('Status 0: Now sending length={} index={} end={}\n'.format(payload_size, payload_index, payload_index+payload_size))

        # First, stop listening so we can talk.
        radio.stopListening()

        # Send next chunk
	print('Sending {}'.format(send_payload[payload_index:payload_index+payload_size]));
        radio.write(send_payload[payload_index:payload_index+payload_size])

        # TBD
        # Now, continue listening for the acknowledgement message ACK
        # radio.startListening()

        # Wait here until we get a response, or timeout
        # started_waiting_at = millis()
        # timeout = False
        # while (not radio.available()) and (not timeout):
        #     if (millis() - started_waiting_at) > 500:
        #         timeout = True

        # Describe the results
        # if timeout:
        #     print('failed, response timed out.')
        # else:
        #     read_ack()
            # if data == ACK, status = 1

        # For now, let's assume it was received and move on
        status = 1

        # Remove after i have arduino sending back
        # payload_index += payload_size

        # # If we have stepped through the entire payload, save to database
        # if payload_index >= max_payload_size:
        #     status = 2
        # else:
        #     # otherwise, set status back to 0 so we transmit again
        #     status = 0

    # receiving data
    elif status == 1:
        print('Status 1: Receiving data from Sender Arduino; then send next chunk or save\n')

        # Now we wait to get the data back from the sender Arduino
        radio.startListening()

        # Read the file data and save it to our dict
        read_file_data()

        # Now check if we heard from everyone. If so, send the next chunk of data
        # Should add a timeout here, so in case we don't hear from a child, we can move on
        if check_responses():
            # Step through the payload...
            payload_index += payload_size

            # Now we start a new round of transmission
            transmission_id += 1

            # If we have stepped through the entire payload, save to database
            if payload_index >= max_payload_size:
                status = 2
                # status = 3
            else:
                # otherwise, set status back to 0 so we transmit again
                status = 0

    # saving data
    elif status == 2:
        print('Status 2: Received all image data back, saving to DB\n')
        # Now we save our array to our web app endpoint, to the DB

        # after successful save, set status back to 0
        # but how do i wait for successful save response from DB?

        # reset everything:
        select_image()
        payload_index = 0
        received_payloads = dict()
        transmission_id = 1
        status = 0

    elif status == 3:
        print('Status 3: Temp status til web app is hooked up. Just chilling.\n')

    # error; status equals something strange
    else:
        print('Status error! {}\n'.status)

    time.sleep(0.1)
