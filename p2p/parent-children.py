
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Script for Raspberry Pi for sending image data to one half of an arduino radio pair
# and receiving image data back from the other half of that pair.
#

from __future__ import print_function
import time
import io
from io import BytesIO
from RF24 import *
import RPi.GPIO as GPIO
from PIL import Image
from array import array
import requests

########### RADIO CONFIGURATION ###########
# Setup for GPIO 15 CE and CE0 CSN for RPi B+ with SPI Speed @ 8Mhz
radio = RF24(RPI_BPLUS_GPIO_J8_15, RPI_BPLUS_GPIO_J8_24)

# Count up so we send a packet to all children
txNum = 0
# Count total number of transmission per packet per group of children
transmission_id = 1
# Increment text_id so we can step through our array of image data
text_id = 0
# Our image data
texts = [
".,:;;;,,,'''.",
".,okO0Okxdollll'",
".,oO0000Okkxocccc;.",
".,:loxO000OOOOOkkxdoodoc;.",
";xO0KKKK00OOOkkkkkOOOOOkxdl,.",
".'xKKK0000OOOkkkkOO0K00Oxdooll,",
"...',;:cllodxkkOKKKKKK000000OO00KKK0Okxdoolc,",
".':ldkO0KKXXXXXXXXXXXXXXXXXXKKKKKKKKKKKKKKKK000OOkxolc:;,'...",
".,:oxOKXNNXNNNNNNNNNNNNNNXXXXXXXXXXXXXKKKKXXXXXXXXXXXXXXXXXKKK000kxol:,'",
"..;cox0KXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXNNNNNXXXXXXXXNNXXXXXXXKKKXXKK0Oxoc:;..",
".';coxOKXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXXXXXKKKKKKKKKK0KKK00kdlc;,..",
".';coxOKXXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXXXXXNNNNNNNNNNNXXXXXXXKKKKKKKKKKKKKK000000OOxoc;.",
"..',;:clllodk00KKKKXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXNNNNNNXXXXXXKKKKKKKKKKKKKKKK00000000000ko:'.",
"..,:clodxk0KKKKXKKKKKKKKK00000000KKXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXXXNNXXXXXXKKKKKKKKKKKKKKKK000000000000000Odc,.",
".,cdk00KKKKKKXXXXXXXXXXXXXKKKKK00OOkkkkkO0KXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXXXXXXXXXXXKKKKKKKKKKKKKKK00000000KKKKKKKKK000xl,.",
".;dO0KKKKKKKKXXXXNNNNNNNNXXXXXXKK0OOkxxxxdddddOXNNNNNNNNNNNNNNWWWWWNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXXXXXXXXXXKKKKKKKKKXXXKK0000000000KKKKKKKK0000OOxl;.",
"'ckKKKKKXXKKXXXXNNNNNNNNNNNNNNNXK0OOkxxdddooooood0NNNNNNNNNWWWWWWWNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXXXXXXXXXXKKKKKKKKXNNNXK0OOOO00000KKKKKKKK00OOOOOOOxl,.",
".;dOKKKKXXKKKKKKXXXXNNNNNNNNNNNNNXK0OkxdooooooooooodkKXXXXNNNWWWWWWWNNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXXXXXXXXXKKKKKKXXXXNNXXXKOkkkOOOO0000KKKKK00OOOOOkkkkkdc'.",
".,lx0KKKKKXXXKKKKKKKKXXNNNNNNNNNWWNXKOxddoooooollllllllx0000KXNNWWWWWWWNNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXXXXXXXKKKKKKKKXXXXXXXXX0OkkkOOOOOOO000000000OOOOkkkkxxkxo;.",
".,lx000KKKKKKKKKKKKKKKKXXXXXXNNNNNNWNK0kxdooollllcc::::::ccloox0XNWWWWWWWNNNNNNNNNNNNXNNNNNNNNXXXXXXXXXXXXXXXXXKKKKKKKKKKKKKKXXNNXKXX0kkkkOOO00000OO00000OOOOOOkkkxxxxxxo:.",
".cx0000KKKKKKKXXKKKKKKKXXXXXXXXXXXXXXX0kxdoolllllc:;;;;;;;;;;:clx0XWWWWWWWNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXXKKKK000KKKKKXXNXXXXK0kkkkOO0000000000O00OOOOOOkkkxxxxxxxxd:.",
".ck0000KKKKKKKKKKKKKKKKXXXXXXXXXXXXKXXK0kdoolllllc:;;;;;;;;,;;:cox0XNWWWWWWWNNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXKK00OOO0KKKKXXNXXXK0OkkkkkOO000000000O00OOOOkkkkxxxkkkkkkxkd:.",
".d000KK0KKKKKKKKKXXKKKKXXXXXXXXXXXXKKK0Okdololllc:;;;;;;,,,;;:clok0XNWWWWWWWWWNNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXKKK0OOOO0KKKXXNNNXK0OkkkkOOOOO0000000OOOOOOOOkkkkkkkkkkkkkkkkxd,",
".d00000KKK00KKKXXXXXKKXXXXXXXXXXXKKKKK0Oxdooolll:;,,,,,,,;;;:cloxO0XNNWWWWWWWWWWWWWWNNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXKKK00OOOO0KKKXXNNNX0OkkkkkkOOO000000000OO00OOOOkkkkkkkkkkkkkkkkkdc.",
".d0000000KK0KKKKXXXXXXXXXXXXXXXXXKKKKK0Okdoooolc:,,,,,,;;;::codxk0KXNNNNNNWWWWWWWWWWWWNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXKKKK000OOO00KKXXNNNXKOkxkkkkOOO000000000000000OOOOOOOOOOOOkkkkkkkkxo;.",
".oOO000000KK0KKKKKKXXXXXXXXXXXKKKKKKKK00kxdooolc;,,,,;;;;::loxkO00KXNNNNNNNWWWWWWWWWWWNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXKKKKKK0000O00KKXXXKKXKOkxxxkkOOO000000000000000OOOOOOOOOOOOOkkkxkkkkxdl'",
".lOOO0OO000000KKKKKXXXXNXXXXXXXKKKKKKKK0kxooollc;;;;;;;::cloxkO0KKXXNNNNNNNWWWWWWWWWWWWNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXKKKKKKKKK000000KKXXKKXKOkxdxkkkOO0000000000OOOOOOOOOOOOOOOOOOOkkkkkkkkkxd;.",
".,lkO0O000000000KKKKXXXXXXXXXXXXXKKKKXKKOxdoolllc;;;;;;::clodkO00KXXNNNNNNNNWWWWWWWWWWWNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXKKKKKKKKKKK00000KXXK0KKOxddxkkkOO0000000OOOOOOOOOOOOOOOOOOOOOOOkkkkkkkkkkxl'",
".cdkOOOO0000KK0KKKKKKKXXXXKXKKKKKKKKXXX0Okdoollc:;;;;:::clodkO0KKXXXNNNNWWWWWWWWWWWWWWNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXKKKKKKKKKKKK000KXNNKO0KkdddxxkOO00000000O00OOOOOOOOOOOOOOOOOOOkkkkkkkkkkkkkd;.",
".:dkOOO0000000KKKKKKKKKKKKKKXXXKKKKKXXXK0Okxolllc:;;;:::clodxO0KKXXXNNNNNNWWWWWWWWWWWWWWNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXXXXXXXKKKKKKKK0KXNXX0O0kdddxxkkkO000000OO0OOOOOOOOkkkkkkOOkkOkkkkkkkkkkkkkxkxc.",
".;oxOOOOOOOO0000000KKKKKKKKKKXXXKKKKKKXXK0Okdolll:;;;::cclodkO00KXXXNNNNNNWWWWWWWWWWWWWWWNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXXXXXXXXXKKKKKKKKXXXXKO00xxxxxkkkOOO000OOOOOOkkkkkkkkkkkkkkkkkkkkkkxkkkxxxxxkxxd,",
".,oxkOO0000OOO00KKK00KKKKKKKKKXXXKKKKXXXXK0Oxolllc:;;::ccldxkO00KKXXNNNNNNNWWWWWWWWWWWWWWNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXXXXXXXXXXXKKKKKKKXXXXXX000kxxxxxxkOOOOOOOOOkkkkkkkkkkkkkkkkkkkkkkxxxxxxxxxxxxxxxxx:.",
".,lxkkOO000KK0000000000KKKKKKKKKXXKKKKKXXKK0kdolcc:;;::clodxkO0KXXXNNNNNNWWWWWWWWWWWWWWWWWWNNNNNNNNNNNNNNNNXXXXNXXXXXXXXXXXXXXXXXXXXXXXXXXXKXKKXNXXXXKOOOkxxxdxkOOOOOOOOkkkkkkkkkkkkkkkkkkkkkkxxxxxxxddddddddxxxxl.",
"'lxkkOOO000KKK0OO0000K00KKKKKKKKKKXXXXXXK0Okxolcc::::clodxOO0KKXXNNNNWWWWWWWWWWWWWWWWWWWWWWNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXXXXK0OkxxxkOKXXXXXKKKKXNXXXXK0OkkxxxdxkkkOOOOkkkkkkkkkkkkkkkkkkkkkkkkxxxxdddddddddddddxxxo,",
".cdxkkOO000KKKKXK0OO00KKKKKKKKKKKKXXXXXXK0Okxdolc::ccloxkO00KXXXNNNWWWWWWWWWWWWNNNNNNWWWWWWWWNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXK0kdlc:;;;;:cdk0XKKKKKXNXXXXK0kxxxxdddxkkkkkkkkkkkkkkkkkkkkkkkkkkkkxxxxxdddddddoooooooddxxo;",
".;oxxxkOO000KKKKXXXK0OOO000KKKKKKKKKXKKK0OOkxdolccccoxkO00KKXXNNNNWWWWWWWWWWWWWWNNNNNNNNNWWWWWNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXXKkooc;::;,',,,,;cx0KKKKXXXNXXK0Oxxxxdddxxxkkkkkkkkkkkkxxkxkkkkkkkkkxxxxxddddddooooooooooddxxd;.",
"'codxkkOO00KKKKKXXXXXXK0OkkkOO00KKKKK00OkxddolccccoxkkkxddxxxOKNNNNNWWWWWWWWWWWWNNNNNNNNNWWWWWWNNNNNNNNNNNNNNNNNNNNNXXXXXXXXXKOddoc,'''...',..',lk000XNXXXXK0Okxxdxddxxxxxkkxkkkkkxddkkkkkkkkkkxxxxxdddddddooooooooooooddxxd:.",
".,lodxxkO000KKKKXXXXXXXXXXKOkxkkkOOkkkkxdoollccccldkOkdooc;,;::;cx0NNNNWWWWWWWWNNNNNNNNNNWWWWWWWNNNNNNNNNNNNNNNNNNNXXXXXXXXXKXKklldl;'''..''',...',lkO0XNXXXXK0Okxddxxxxxxxxxxxxxkkkxdxxkkkkkkkxxxxxdddddddoooooooooooooooodxxx:.",
".:loddxOO00KKKKKXXXXXXXXXXXXKK000OOkxddoolllllodxkOOkdlodl:::cl;'',ck00KNNNNWWWNNNNNNNNNNWWWWWWWNNNNNNNNNNNNNNNXXXXXXXXXXXXKKKKKd:cc;,,,'.',,....'',cdxOKXXKKKK0Oxxdddxxxxxxxxxxxxxkkkkxxxxxxxxxxxxxddddddooooooooollloooooodxxxx:.",
"'cooddxkO00KKKKKXXXXXXXXXXXXXXXXXXXKK0OkkkkkOO000KX0olddxxoldxl;,,'',:odkKXNNNWWNNNNNNNWWWWWWWWWWNNNNNNXXXXXXXXXXXXXXXXXXXXXKKKKKko:';:;'''''......',:lokKXXXKKK0Okxddxxxxxxxxxxxxxxkkkkkxxxxxxxxxxxxdddddoooollloooolllooooodxxxxd;",
"'cooddxOO00KKKKKKXXXXXXXXXXXXNNNNNNNXXXXXXXKXXXXXXXNk:cdddc;;cdc,,;;,,,;cdOXNNNWWNNNNNNWWWWWWWWWWWNNNNXXXXXXXXXXXXXXXXXXXXXXKKKKKKKkl:,,'...........';cccoOKKXKKK00kxxxxxxddxxxxxxxxxkkkkkkkxxxxxxdxxxddddoooooollllooollolloodxxxxxd;",
".,cooddxkO000KKKKKXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNOclool,,loc;;,'','';cokKNNNWWNNNWWWWWWWWWWWWWWNNNXXXXXXXXXXXXXXXXXXXXXXKKKKKKKKK0kdl;'''''....',;:ccclkKKKKK000Okxxxxxdddxxxxxxxxkkkkkkkkxxxxxxxxxxddooooooooolloolloollodxxxxxxxd,",
".;looddxkOO00KKKKKXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNXd:lol;coc;''''''.';clkKNNNNWNNWWWWWWWWWWWWWWNNNXXXXXXXXXXXXXXXXXXXXXXXKKKKKKKKKKK0kdc::;,,,,;::clloooxO0KKKK000kkxddxdddxxxxxxxxxkkkkkkkkxxxxxxxxxddoooooooooooooooollodxxxxxxxxxo'",
".;looddxkOO000KKKKXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNKo:::;;,'.......';cldOKNNNNWWWWWWWWWWWWWWWWNNNXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXKKOkdollooooooddxxxxkO0KKKKK0Okxxxxddddxxxxxxxxxkkkkkkkxxxxxxxxxdddoooooooooooooolloodxxxxxxxxxxl.",
".;lloodxkOO0000KKKKXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNXOoc;,,'....'',:lookKXNNNWWWWWWWWWWWWWWWWWNNNXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXKK0OOkkkkkkkkkOOOOOOO00KKKK00Okkxxdxddxxxxxxxkkkkkkxxxxxxkkxxxdddooooooooooooooloodxxxxxxxxxxxxc.",
".;cllodxkkOO0000KKKKXXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNKkoc:;;;:clodxxk0XNNNNWWWWWWWWWWWWWWWWNNNNXXXXXXXXXXXXXXXXXXXXXXXKKKXXXXXXXXXXXXXKK000OOO00O0000000OOOO0000000Okxxxkxxxxkkkkkkkkkkxxxxxxxxxxxddddddoooooooooooooodxdxxxxxxxxxxxd,",
".,:cllodxkkOO000KKKKKXXXXXXXXXXXXXXNNXNNNNNNNNNNNNNNNNNNNNNNNNNNNNK0OkxxxxkkOO0KXXNNNWWWWWWWWWWWWWWWWWNNNXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXKKKK000000000000000OOOkOO000000Okkkkkkkkkkkxxxxkkkkkkkxxxxxxddddddddoooooooooooddxdddxxxxxxxxxxxo.",
"':ccloodxkkOO000KKKKXXXXXXXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNWNNNXXKKKKKKKKKXXNNNNNWWWWWWWWWWWWWWWWNNNXXXXXXXXXXXXXXXXXXXXXXXXXXKKXXXXXXXXXXKKKKKKKK0000000000000OOOOOOOOO000OOOOOxxxkkkkxxxxkkkkkkkkxxxxxddddddooooooooooodddddddddxxxxxxxxxxx:",
".;:clloddxkkOO000KKKKXXXXXXXXXXXXXXXXXNXXXNNNNNNNNNNNNNNNNNNNNNNWNNNNNXXXXXXXXXXNNNNNNNWWWWWWWWWWWWWWNNNXXXXXKKXXXXXXXXXXXXXXXXXXKKKKXXXXXKKKKKKKKKKKKKKKKKKK000000000OOOOOOOOOOOOOOOOkxxk0Okxxxxxxkkkkkkkxxxxxddddooooooooddddxddddddddxxxxxxxxxxo.",
".,:ccloodxxkOOO0000KKKXXXXXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXXNNNNNNNNNNWWWWWWWNNNNXXXXKKKKKKKKKKKKKKKKKKXXXKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK000000000000000OOkxxkkkkkkkkkO0OOkxxxxxxkkkkkkkkxxxxdddoooooodddddddddddddddxxxxxxxxxxxc.",
".,::clloddxxkOOO0000KKKXXXXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXNNNNNNNNNNNNNNNNNXXXKKKKKKK000000OO0000OOOO0000KKKKKKKKKKKKKKKKKKKKKKKK0KKKK00000000000KKKK00Okxxddxxxxxxxkkkxxddddxxxkkkkkkkkxxdddooolooddddddddxxxddddddxxxxxxxxxxd,",
".;:cclooddxkkOOOO000KKKKXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXXXXXKKKKKKKKKKKK00000000000000000OOOOOO000KKKKKKKKKKKKKKK0000000000000000KKKKKKKK00Okkxddddddddxxxdddddddxxxxxxxxxxxddoollloddddddddddddddddddddxxxxxxxxxxl.",
".,;:ccloodxxkkOOOO000KKKKXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXXKKKKKKKKKKKKKKKKK0000000000000OOOOOOOOOOOOOOOO000000KKKKKK0000000000000000KKKKKKKKK00OOkkxxdddddddddddoodddddddddddddoolllloodddddddddddddddddddddddxxxxxxxxd;",
".';::clloddxkkkOOOO0000KKKKXXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXXKXXXXXXXXXXXXXXXXKKK000OOOkkkkOOOOkkkOOOOOkkkkkkkkkkOO00000000000000000000000KKKKKKKKK000OOkkxxxdddooooooooddooooloolllllllloddddddddddddddddddddddddddddxxdxxxxo.",
".,;:ccloodxxkkkkOOO0000KKKKKKXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXXKKKKKKXXXXXXXXXXXXXXKKKK00OOOOOOOOOOOOOOOOOOkkkkkkkkkkxxxkkOO0000000OOOOOOO00000KKKKKKKK0000OOkkkxxxxdddoolllloolllllccccclloooddddddddddddddddddddddddddddddddddddd;",
".',;:clloddxkkkkkOOO00000KKKKKKKXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXXXKKKKKKKXXXXNNNNXXXXXXKKKK0000000OOOOOOOOOOOkkkkkkkkkkkkxxxxdxxxkkOOOOOOOOOOOOOO000KKKKKK00000OOOkkkkkxxxxdddooolllllllllllloooddddddddddddddddddddddxddddddddddddddddxl.",
".',;:clloddxxkkkkOOO000000KKKKKKKXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXKKKKKKKKXXXNNNNNXXXKKKKKKK0000000000OOOOOOOOOOOkkkkkkkkkkkkxxxxddddddxkOOOOkkkkOOOOO0000000000OOOkkkkkkkxxxxxxddddddoooooooooooodddddddddddddddddddddddddddddddddddddddddd,",
".';::clloddxxxkkkOOO000000KKKKKKKKXXXXXXXXXXXXNNNNNNNNNNNNXXXXNNNNNNNNNNNNNNNNNXKKKKKKXXXXXXXXXXXXXXKKKKK0000000000OOOOOOOOOOOOOOOkkkkkkkkkkkkkxxxddddoodxxxxxxkkkkkkOOOOOOOOOOOOkkkkkkxxxxxxxxxxxxxxxxddddddddddddddddddddddddddddddddddxxdddddddddddddddddc.",
".,;:ccllooddxxxkkOOO00000KKKKKKKKKXXXXXXXXXXXXXXNXXXXXXXXXXXXXNNNNNNNNNNNNNNNNXKKKKXXXXXXXXXXXXXXXXKKKKK0000000000000000000OOOOOOOOkkkkkkkkkkxxxxxdddddoooddddxxxxkkkkkOOOOOOkkkkkkkkxxxxxxxxxxxxxxxxxxxxxxxxdddddddddddddddddddddddddddddddddddddddddddddddo'",
"..,;:ccllooddxxxkkOOOO0000KKKKKKKKXXXXXXXXXXXXXXXXXXXXXXXXXXXXNNNNNNNNNNNNNNNXXKKXXXXXXXXXXXXXXKKKKKKKK000000OOOOOOOOOOO00OOOOOOOOOOOOOOOkkkkxxxxxdddddddooooooodddxxxkkkkkkkkkkkkkxxxxxxxxxxkkxxkkkxxxxxxxxxxdddddddddddddddddddddddddddddddddddddddddddddddd,",
".',;:clllooddxxxkkOOOO0000KKKKKKKKXXXXXXXXXXXXXXXXXNNNXXXXXXNNNNNNNNNNNNNNNNXKKKXXXXXXXXXXXXKKKKKKK00000000OOOOOOOOOOOOOOOOOOkkOOOOOOOOOkkkkxxxxxddddddddooolllooooddxxxxkkkkkkkkxxxddddddxxkkkkkkkkkkkkkxxxxxxddddddddddddddddddddddddddddddddddddddddddddddd;",
".',::clllooodxxkkkOOOO00000KKKKKKXXXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNXXKKXXXXXXXXXXKKK00000000000OOO0OOOOOOOkkkkkkkkkkkkkkOOOOOkkkkkxxxxxdddddddddooooolllllloodddxxxkkkkkkxxxdollodxxxkkkkkkkkkkkkkxxxxxxxdddddddddddddddddddddddddddddddddddddddddddood;",
".,;::ccllooodxxkkkOOOOO0000KKKKKKXXXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNXXKKXXXXXXXXKKKK000OO000OOOOOOOOOOOOOOOOkkkkkkkxxxxxkkkOkkkxxxxxxxxdddddddddddoooooolccllloodddxxxxxkkkxxxoccloxkkkkkkkkkkkkkkkxxxxxxxxddddddddddddddddddddddddddddddddddddoooooooood;",
".',;::ccllloodxxxkkOOOOOO000KKKKKKKXXXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNXKKKKXXXKKKK000000OOOOOOOOOOOOOOOkkkkkkOOkkkkxxxxxddxkkkkkxxxxxxxxddddddddxdddddoooooolcclloooddddxxxkkkkkxoccodxkkkkkkkkkkkkkkxxxxxxxxxddddddddddddddddddddddddddddddddddoooooooooooo;",
".',;::ccllloodxxxkkkOOOOO000KKKKKKKKXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNXKKKKKKKKKKK0OOOOOOkkOOOOOOOOOkkkkkkxxxkkkkkkxxddddxxkkkxxxxxxxxxxddddddxxxxdddddoooooollccllooddddxxxkkkkkkxdddxxkkkkkkOOkkkkkxxxxxxxxddddddddddddddddddddddddddooooodddoooooooooooooo,",
"..';::ccclloodxxxkkkOOOOO0000KKKKKKKKKKKKKXXXXXXXNNNNNNNNNNNNNNNNNNNNNNXKKKKKKKKK0000OOkkkxxxxxkkkkkkkkkkxxxxxxxxxxxxxxxxxxxkkkxxxxxxxxxdddddxxxxxxdddddddoooooollcclloddddxxxxkkkkkkkkkkkkkkkkOOkkkkkxxxxxxdxdddddddddddddoooooooddddddooooooooooooooooooooooc.",
"..',;:cccllooddxxkkkOOOOO00000KKKKKKKKKKKKKKXXXXXXXNNNNNNNNNNNNNNNNNNNXKKKKKKKKK00OOOkkkxxxdddddddxxxxkxxxxxxkxxxxxxxxxxxxkkkkkxxxxxxxxxxxxxxxxxxxxxddddddooooooollccloodddddxxxxxxkkkkkkkkkkkkkkkkkkxxxxxxddddddddddddddoooooooooddddddoooooooooooooooooooool,",
"..',;:cccllloddxxkkkOOOOOO0000000KKKKKKKKKKKKKXXXXXXXNNNNNNNNNNNNNNNNXKKKK0000000OOOOkkxxddooollooodxxxxkkkkkkkkxxkkxxxxxkkkkkkxxxxxxxxxxxxxkkxxkkxxxxddddooollooollccloodddddddxxxxxxxxxkkkkkkkkkkkxxxxxddddddddddodddooooooooooooodddooooooooooooooooooolll:.",
"...,;::ccllloodxxkkkkOOOOOO0000000KKKKKKKKKKKKKKXXXXXXNNNNNNNNNNNNNNNK000000000OOOkkkkxdolcc::::cclodxkkkkkkkkkkkkkkxxdxOkkkkkkkxxxxxxxkkkkkkkkkkkxxxxdddooolllooollcccllooodddddddxxxxxxxkkkkkkkkxxxxxddddddddddoooooooooooooooooooooooooooooooooooooooolllc'",
"...',;::cccllodxxkkkkOOOOOOO0000000000KKKKKKKKKKKKXXXXXNNNNNNNNXNNNNX0O0000000OOOOkkxxdoc::::::::cclodkOOOOOkkkkkkkkkxxOOOkkkkkxxxxxxxkkkkkkkkkkkkxxxxxdddoolllloollc:cclllooooddddddddxxxxxxkkkxxxxxddddddddoooooooooooooooooooooooooooooooooooooooooolllll;.",
"...',;:::ccclodxxxkkkkOOOOOOO0000000000000000KKKKKKKXXXXXXXXXXXXXXXXKOkOOO0000OOOkkkxdoc::::;:;;:cclodxOO0OOOOkkkkkkkkkOOkkkxxxxxxxxxxxkkkkkkkkkkkkkxxxxdooollllllllc:::clllooooddddddddxxxxxxxxxxxxdddddddooooooooooooooooooooooooooooooooooooooooolllllllc.",
"....',;::ccclodxxxxkkkkOOOOOO00000000000000000KKKKKKXXXXXXXXXXXXXKKK0OkOOO000OkkOOOkxol::::;;;;;:cloodkO0000OOOOOOOOkkkkkxxddooooooddxkkkkkkkkkkkkkxxxkxdoollllllllll:::cclllooooodddoddddxxxxxxxddddddddoooooooooooooooooooooooooooooooooooooooooolllllllc,",
"....',;;::ccloddxxxxkkkkOOOOOO000000000000000KKKKKKKKKKXXKKKXKKKKKXK0OkxkOO0OOOOOOOkxoc::::;;;;;:codxxkO0KKK00000OOOkkkxdoolcc::::cllodxkOOOOOOkkkxxxxxxxollllllllllc::::cccllooooooooooddddddddddddddddooooooooooooooooooooooooooooooooooooooolllllllllll:.",
".....',;::cllooddxxxxkkkkOOOOOOOO0000000000KKKKK000KKKKKKKKKKKKKKKKKOOxdxkkOOOO000OOkdl::::;;;;;:coxkOO0KKKKK00000OOkkxdlcc:::;;;::cllodkO000OOOkkxxxddddollllllllllc:;:::cclllllloooooooooooodddddddooooooooooooooooooooooooooooooooooooloooollllllllllcc,",
"......',;:cllloodddxxxkkkkOOOOOOOO0000000KKKKKKK000KKKKKKKKKKKKKKKKKOOkkkkkOOOO0000Okxoc:::;:::cloxkO0KKXXKKKK0000OOkxdlc::::;;;;;;:coodxO0000OOkxxxddddolllllllllllc:;:::ccclllllllloooooooooooooooooooooooooooooooooooooooooooooollloollloollllllcccccc;.",
"......',;:ccllloodddxxxkkkkkkOOOOOO000000000000000000000000000KKKKK0OOOkkkOOOO00KK00OkxdollccclodxkO0KXXXXKKKK000OOOkxoc::::;;;;;;;:cldxkO0KKK0Okkxxdddoollllllcccll:;;:::cccclllllllllloolllooooooooooooooooooooooooooooooooooolllllooolccloolllc:;;;;;;.",
".......,;::ccllooodddxxxkkkkkOOOOOOOOO00000000000000000000000KKKKKK0OOOkkOO00000K000OOkkkkkxxxkkO00KXXXXXKKKKK000OOOkdoc::::;;;;;,;;:ldxkO0KKK0Okkxxdddolllllccccccc:;;:::cccccllllllllllllllllooooooooooooooooooooooooooooooollllcclllllc:clooool:;;;;;'.",
"......';;:ccclloodddxxxkkkkkOOOOOOOOOOO0000000000000000KKKKKKKKKKK0OkkkkOOO0000000OOOOOOOO000KKKXXXXXXXKKKKK0000OOOkxocc:::;;;;,,;;:ldkO0KKXK0OOkxdddoolllcccccccc:;;::::::ccclllllllllllllllllooooooooooooooooooooooooooolllllcccccclcclccclodoclolc:;.",
".......';;::ccloodddxxxkkkkkkOOOOOOOOOOO0000000000000KKKKKKKKKKKKKK0kkkkkOOOOOOOOOOOOOOOOO000KKKKKKKKKKKKK0000000OOkxdocc::;;;;;;;:coxkO0KXXK0Okkxdooollllcccccccc:;;::::::ccccllllllllllllllllloooooooooooooooooooooooollllllc:cccccccccclllodl;,:llc;.",
".''....',;::clloddxxxxkkkkkkkkOOOOOOOOOO0OO0000000KKKKKKKKKKKKKKKXKOkkkkOOOOOOkOOOOOOOOOOO000000000KKK0000000000OOkkkxolcc::;;;;:codk0KKXXXK0Okxddollllccccccccc::;::::::cccccllllllllllllllllllloolllooooooooooooooollllllcc:ccc:ccccccccllldoc;,,::'",
".''''.....,;:lloddxxxxxxxkkkkkkOOOOOOOOOOOO000000KKKKKKKKKKKKXXXXXX0kkkkkOkkkkkkkkOOOOOOOOOOO0000000000000000000OOOkkkkxxdoolloodxkO0KKXXK0Okkxdoolllllcccccccc:::::::::ccccccllllllllllllllllllllllllloooooooooooollllllcc:::cc::ccllcc:ccccod:,;,,;.",
".''''....',;cloddxxxxxxxxxxkkkkkkOOOOOOOO0000000KKKKKKKKKXXXXXXXXXKOxkkkkkkkkkkkkkkkkOOOOOOOO00000000000000000OOOOOkOOOOOOOOOO000KKKKKK0Okkxddoolllllcccccccc::;::::::::cccccllllllllllllllllllllllllllooooooooooolllllcc:;;::,,:::clc::::::ld:';;,,.",
".,'...''',;clooddddddxxxxxxxkkkkkkOOOOO00000000KKKKKKKKKXXXXXXXXXXKkxkkkkkkkkkkkkkkkkOOOOOOOOO0000000000000OOOOOOOOOOOOOOOOO000000000Okkxxdooollllccccccccc::;::::::::ccccccllllllllllllllllllllllllllooooooooolllllccc:;;,:;.';:;,:c::;;;:cl:',c,.",
"........';clooddddddddxxxxxkkkkkOOOOO000000000KKKKKKKKKKXXKKXXXXXX0kxxkkkkkkOkkkkkkkOOOOOOOOOO0000000000OOOOOkOOOOOOOOOOOOOOOOOOOkkkxxdddoollllccccccccc:::::::::::::ccccccllllllllllllllllllllllloooooooooollllllccc::;,,:;'.',..,;;;;:c:,;c',;.",
"..   ...;clloooddddddxxxxxkkkkOOOOO00000000000KKKKKKKKKKKXXXXXXXXXKkxxxkkkkkkkkOOOOOOOOOOOOOOOOO0OOOOOOOOOOkkkOkkkkkkkkkkkkkkkkxxxdddoooollllccccccccc:::;:::::::::ccccccllllllllllllllllllllllllooooloooollllllccc::;;;:c;;,,;,;;,;:;,'..,:;'.",
"..;ccllloooddddxxxxkkkkkOOOOO0000000000000KKKKKKKKKKKKKXXXXKKKOxxxxkkkkkkkkkkOOOOOOOOOOOOO00OOOOOOOkkkkkkkkkkkxxkkxxxxxxddddddoooollccccccccc:::::;:::::::::cccccclllllllllllllllllllllllooooolllllllllllccc:::::c:;;;'.'',;'.,...';::,.",
".,:ccllloooddxxxxxkkkkkOOOOO000000000000000000KKKKKKKKKKXKKKKKOxddxxxxxxkkkkkkkkOOOOOOOOOOOOOOOOOkkkkkkkkkxxxxxxxxxxdddddooooollllcccccccc::::;::::::::::cccccclllllllllllllllllllllllloooooolllllllllccc::::::c:,,,,,'...,,',,,;::;'.",
"..;::cllloodddxxxxxkkkkOOOOOO000000000000000000000KKKKKKKKKKKKK0OxdddxxxxkkkkkkkkkkkkkkOOOOOkkkkkkkkkkkxxxxxxxxxxxxdddoooolllllccccccc:::::;;;:::::::::::cccccllllllllllllllllllllllooooollllllllllllccc::::::c:;;,,,,,,'''',;;;,'''.",
".',::ccllooddxxxxxxkkkkkOOOOOOOOO0000000000000000000KKKKKKKKKKKK0Oxdddddxxxkkkkkkkkkkkkkkkkkkkxxxxxxxxxxddddddddoooooolllllcccccc:::::;;;;::::::::::::cccccllllllllllllllllllllooooooooolllllllllllcc:::::::::;;;,,,,,'''';::c:;;,.",
"..,;::ccllooddxxxxxkkkkkOOOOOOOOOOO0000000000000000000000000KK0KKKOxdoodddxxxxxxxxkkkkkkkkkkxxxxxxxdddddooooooooolllllcccccc::::::;;;;;::::::::::::::ccclllllllllllllooolloooooooooooollllllllllcc:::::cc::;;;;,,,,''..';::cc,','.",
"..';;::cclloddxxxxxkkkkkOOOOOOOOOOOOOO0000000000000OO00000000KKKKKK0kxoooodddddxxxkkkkkxxxxxxxdddddoooooooooollcccc:::::::::::;;;;;::::::::ccccccccclllllllloooooooooooooooooooooooollllllllllcc::cccc:::;;;,,,,,''..'::,;:,...",
"..... .   ............,;;::ccloodxxxxxkkkkkOOOOOO00000OOOOOOOOO0000OOOOOOO000000KKKKKKKK0kdooloooddddddddddddooooollllloooollllcc::::;;;;;;;;;;;;;;::::::ccccccccllllllllooooooooooooooooooooooooooolllllllllllcccccc::::;;;;,,,,'''...,cc,',;..",
"..',;;;'...   ...';;,'......',;:::ccloddxxxxkkkkOOOOO00000OOOOOOOOOOO000OOOOOOOOO0000000KKKKKKKK0kxoolllllllllllccccccccllllllcc:::::::;;;;;;;;;;;;:::::ccccccclllllllllloooooooooooooooooooooooooooooolllllllllllcccccllc:::;;;,,,,,''..';ccc:'';;.",
"..',;::ccc;'...   ..,;cc:;,,'.'''.',;;:::cloddxxkkkkOOOO0000OOOOOOOOOOOOOO0OOOOOOOOOOOOOO0000000KKKK000Okxdolccc:::::::::ccccc::::::;;;;;;;;::::::::cccccccllllllllllllloooooooooooooooooooooooooooooooolllllllllllllcccccccllc:;;;,,,,,'''';loc::'..'.",
"..',;;;:cclc;.........,:ccc:;;;,'..''..',,;;:cloddxxkkkOOOO000OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO000000000000000OOkxddolllccccc:::::::::::::ccccccclllllllllllllloooooooooooooooooooooooooddoooooooooooooooooolllllllllllllcccccc:::c::;,'''',,;;,,'..,;...",
".',,;;:::ccllllccc:;,,,,;;;:::::;;;,',,....'',;;:cloddxxkkOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO0000000000OOOOOOkkkxxdddoooooooolloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooollllllllllllllcccccc:::;;;;::::;;;;,......';'",
"..',,;;;::ccclllooooolc:;;;;;;;:::::;:;;;;,'.....',;;:clodxxkkOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO00000000OOOOOOOOOOkkkxxxddddddooooooooooooodddddddddddddddddoooooooooooooooooooooooooooooooooooooooollllllllllllllccccc::::;;;,'',;;,...........'.",
"...',,;;::::ccclllooddddolc:::::::::::;;;:;;;;;,'. ...',;;:cloddxxkkkkkkkkkkkOOOOOOOOOOOOOOO000000000OOOOOOOOOOOOOOOOOOOOOOOOOOkkkkkxxxxddddddddddddddddddddddddddddddddooddoooddoooooooooooooooooooooooooooooollllllllllllllcccccc:::;;,,,'''..............",
".',,;;;:::cccllllooodddoolcc:::::::::::;;;;;;,,;:;.. ...',;;:clloodddxxxxkkkkkkOOOOOOOOOOOO0000000000000OOOOOOOOOOOOOOOOOOOOOOOkkkkkkkkkxxxxxxxxxxxxxddddddddddddddddddoooddoooddoooooooooooooooooooooooooooolllllllllllllllcccccc::;;,,,''''.............",
".',;;;:::cccclllllooodddoollcccccccccc::;;;;;;,',cc;'.. ...',;;::ccllooddxxxkkkkkOOOOOOOOOOOO0000000000000OOOOOOOOOOOOOOOOOOOOOOOkkkkkkkkkkkkkkkxxxxxxxxxxddddddddddddddoooddoooooooooooooooooooooooooooooooollllllllllllcccccccc:::;;,,'''...............",
".,;;;;::ccccllllllooodddoooollllllccccc:::;;;,,'.';c:,,. ...'',;;;::ccllooddxxkkkkOOOOOOOOOOOOO000000000OOOOOOOOOOOOOOOOOOOOOOOOOOOOkkkkkkkkkkkkkkxxxxxxxxxxddddddddddddooooooooooooooooooooooooooooooooooolllllllllllllccccccc:::;;,,'''...............",
".,;;;::ccclllllloooooodddooooooolllllccc:::;;;,'...':cc;. ....',,;;:::cclloodxxxkkkOOOOOOOOOOOOOOOOOOOOOOOOkkkkkkOOOOOOOOOOOOOOkkkkkkkkkkkkkkkkkkxxxxxxxxxxxxdddddddddddooooooooooooooooooooooooooooooooollllllllllllllccccccc::;,,'...................",
".,::::ccllllllooooooooooooooooooolllllcccc:::;;,'....,::;,......',,;;:::ccllooddxxkkkkkkkOOOOOOOOOOOOOkkkkkkkkkkkkkkkkkkkkkkkkxxxxxxxxxxxkkkkkxxxxxxxxxxxxxxddddddddddddooooooooooooooooooooooooooooooolllllllllllllllcccccc::;,'.....................",
".;::ccclllllloooooooooooooooooooollllccccc::::;;,'.....';;;'......',,;;;::cccllooddxxxkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkxxxxxxddxxxxxxxxxxxxxxxxxxxxxxxxxxxdddddddddddoooooooooooooooooooooooooooooooollllllllllllllcccccc::;,'...',,;;;;;::::::::::;'.",
".;::ccclc::cloooooooooooooooooolllllcccccc::::;;,'.......',,'.......',,;;:::cclllooddddxxxxxxxkkkkkkkkkkkkkkkkkkkkkkkkkkxxxxxxxxxxxxxxxxxxkkkkkxxxxxxxxxxxxxdddddddddoooooooooooooooooooooooooooooollllllllllllllccccccc::;,..',;:cccccllllllllllllllcc:,.",
".;::c:::;;:cooooooooooooooooolllllllcccc::::::;;,''........'''........',,;;::ccc::cloooddddxxxxxxxxkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkxxxxxxxxxxxdddddddddddddddooooooooooooooooooooooolllllllllllllllccccc:::;,..';:llcllloodddooooollllllllllc;..",
".;::;;,,,:loooolllllllllllllllllcccccccc::::::;;,,''...........''.......',,;;;:;..,:looooddddddxxxxxxkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkxxxxxxxxxxxddddddddddddddddddooooooooooooooollllllllllllllllllllcccc::;,'.',:cllllooodddxxdddddoolllllllooll:;'.",
".,;,,'';cooolllllllllllllllllcccccccccc::::::;;;,,''.........  ..'''......',,;;,.',;:looooddddddxxxxxxxxxxxxxkkkkkkkkkkkOOOOOOOOkkkkkkkkkkkkkxxxxxxxxxxxxdddddddddddddddddddooooooooooolllllllllllllllllllllcccc::;;,'..,cllooooddddxxxxxxxxxdddooooooooooolc::;,'.",
".'''',:looollllllllllllllllllccccccccc:::::::;;;,,''.........     ..........',,,'';;;:cloooddddxxxxxxxxxxxxxxxxxxkkkkkkkkkkOOOOOkkkkkkkkkkkxxxxxxxxxxxxddddddddddddddddddoooooooooolllllllllllllllllllllccccc::;;'...';clooddxxxxxxxkkkkkkkxxxxxdddddddddddddolllool:,.",
"..';cllolllllllllllllllllllllcccccccc::::::;;;,,'''........         .........'''';;,,;:clooddddxxxxxxxxxxxxxxxxxxxxxkkkkkkkkkkkkkkkkkxxxxxxxxxxddddddddddddddddddddooooooooolllllllllllllllllllllllllccc:;;;,,....';clodxxxkkkkkkkkkkkkkkkkkkkxxxxxxxxxxxxxxdddolddodo:.",
".,:cllllllllllllllllllllllllccccccc:::::::;;;;,,'''........           ........',',;;,,;:clloodddddddddddddddddddddddxxxxxxxxxxxxxxxxxxddddddddddddddddoooooddooooooooollllllllllllcclllcccccccccccccc:;;,''.....,:lodxxkkkkkkOOOOOOOOOOOOOOOOkkkkkkkkxxxxxxxxxxdokxlcccc;.",
".;cclllllllllllllllllllllllccccccc::::::::;;;;,,,'''........              .....''..'',,,,;cclloooooooooooooooooooooooooooooddddddddddoooooooooooooooooooooooooollllllllllllllccccccccccccccccccccc:::;,'''....';:loxxkkOOOOOOOOOO00000OOOOOOOOOOOOkkkkkkkkkxkxxxxxkkxollllc:'",
".:lcllllllllllllllllccccclcccccc:::::::::;;;;,,,'''........                 ...''.',;,'..',::cclllllllccccccccccllllllllcccccccccccccccccccccccllllllllllllllllllccccccccccccccccccc::::::::::::::;,,......',;cldxkkkOOOOOOOO0000000K0OOOOOOOOOOOOOOOOOOkkkkkkkkxxxkkxdooolllc.",
".:ccccccccllllccccccccccccccccc::::::::;;;;;;,,,''........                    .,''',,,,'...,,;:::::::::::::::::::::cccccc::::::::::::::::::::::::::::::::cccccccc::::::::::::::::::::::::::::;;;;,'.....'.';codxkkOOOOOO0000000000KKKK0OOOOOOOOOOOOOOOOOOOOOkkkkkkkkOkxddddlldl.",
".ccccccccccccccccccccccccccc::::::::;;;;;;;,,,,''........                     .::'.......,;;;,,,;::;;;;,,,,,,;;;;;;;:::::::::::::::::::;;;;;;::::;;:::::::::::::::::::::::::::::::::::::;;;;;,,'........';codxkkOOOOO000000KKK0000KKKK0OOOOOOOOOOOOOOOOOOOOOOOOOkOkkkOkdodxdooxc.",
".:cccccccccccc::::::::::::::::::::;;;;;;;;,,,''.......                         ... ......',::;;,;;:lc;'....'',,;;;;;::::::::::::::::::::::::::::::::::;;;;;;;;::::::::::::::::::;;;;;;;,,,,''..........':ldxxkkOOOO000000KKKKK00000KK00OOOOOOOOOOOO00000OOOOOOOOOOOOkkOxcldxxdxd;",
".:cccccccc::::::::::::::::::::;;;;;;;;;;;,,,'.......                                 ......'',;c:;lo:.......,,,,,,;;:::::::::::::::::::::::::::::::::::::::::::::::::::::::;;;;;;,,,'''''..............:odxkkkkOO0000000KKKKK000000KK00000OOOOOOOOOO00000OOOOOOOOOOOOOkkxdxxddddl.",
".;::::::::::::::::::::::;;;;;;;;;;;;;;;;,,,''......                                    .......;:,;c:'.. ....,;;,,,,,,;:::::::::::::::::::::::::::::::::::::;;;;;;;;::;;;;;;;;;,,,''..........  .';'..';ldxkkkkkO0000000KKKKKK00000KKK0000000OOOOOOO0000000000OOOOOOOOOkkkkxdolood:",
".;::::::::::::::::;;;;;;;;;;;;;;;;;;;;;,,,''.......                                       ...,;'..'..   ....,;;;;;;,,,,;;::::cccccccc:::::::::;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,,,,'''.  .... .....;c:,,;coxkkkOOOO000000KKKKKKKK000KKKK0000000OOOOOO00O00000000OOOOOOOOOOkOOkxdoldxdc.",
".,;;;;;;;:::::::::;;;;;;;;;;;;;;;;;;;;;,,,''......                                          .'........'. ....',,;;;;;,,',,,;;::::::::::::::;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,,,,''''. ...   .....:l:;;cldxkkOOOOO00000KKKKKKKKKKKKKKKKK000000OO0OOOOOO00000000OOOOOOOOOOOkkkxddlldxkx:.",
".,,,;;;;;;;;;;:;;;;;;;;;;;;;;;;;;;;;;;,,,''......                                                 .  ';.........',,;;,,,''''',,;;;;;;;;;;;;;,,,,,,,,,,,,,,,,,;;;;;;;;;;;;;,,,,,''''....  .......:c:;:loxkkOOOOOO00000KKKKKKKKKKKKKKKK00000000OOOOOOOOO0000000000OOOOOOOOkkkxxxxocclod:.",
".,,,,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,,,,'''.....                                                     ... ..........''''''.......'''''''''''''''''''''''''',,,,,;;;;;;;;;;;,,,,,''....   .......,c:::codxkOOOOO0000000KKKKXXKKKKKK0KK00000000OOOkxO0000000000000000OOOOOOOkkxkxdoc:ccc;'.",
".,,,,,,,,;;;;;;;;;;;;;;;;;;;;;;;;;,,,,''.......                                                               ..................''........'''''''.......'''',,,,;;;;;;;;;;,,,,,,''''.   ......'ccccclddxkOOO0000000000KKKXXXKKKK000000000000OOOkOO0000000000000000OOOOOOkkkkkkdlcllol;,,.",
".,,,,,,,,,,,;;;;;;;;;;;;;;;;;;;;,,,,''........                                                                                ..','''''',,;;,,,'.......'''',,,;;;;;;;;;;;;;;,,,,'''...   ....,:::clcldxkOOOO0000000000KKKXXXKKKK0000000000000OO000O0000000000000OOOOOOOOkkkxddlccoooc'.;,'",
".',,,,,,,,,,,;;;;;;;;;;;;;;;,,,,'''.........                                                                                         .................'',,;;;;::::::;;;;;;;;,,,'''......... ...;ccllodxkOOOO000000000KKKKKXXXKK000000000000000O000OO0OOO0000000OOOOOOOOOOkxdlc:clool:,;;;,'",
".',,,,,,,,,,,,,,,,,,,,,,,,,,'''...........                                                                                                          .....''''',,,,,,,'''.........              .;:llodxkOOOO0000000000KKKKKKKKK0000000000000OOOO00OOOOOOO000000OOOOOOOOkkkkdl:;clool:cc;,;;.",
".''',,,,,,,,,,,,,,,,''''''''............                                                                                                                                                        .,clodxkkkOOO0000000000KKKKKKKKK00000000000OOOOOOOOOOOOOO000000OOOOOOOOkkkkdc::clc:cccc;;;,,.",
".''''''''''''''''''''.................                                                                                                                                                           .;loxkkkkkOOOO00000000KKKKKKKKK00000OO00000OOOOOOOOOOOO0000000OOOOOkkkkkkkdc;,;::cllc:;;,'...",
"...................................                                                                                                                                                               .:odkkkkkOOOOO00000000KKKKKKKK00000OOO000OOOOOOOOOOOOOO00000OOOOkkkkkkxxxo:;;:llll::::,..  ..",
"..............................                                                                                                                                                                    .:oxkxkkkkOOOOOOOOO0000KKKKK000000OOOOOOOOOOO00OOOOOOO0000OOOkkkkxxxddxxo::lllll:;:c:'....''.",
".................                                                                                                                                                                           .;dxxxxkkkkOOOOOOOO000000000000000OOOOOOOOO00000OOOO0OO0OOOOOOkkxoloxkkd::lllll:;cl:,''.',:'",
";odxxxxxkkkOOOOOOOO00000000O0000OOOOOOOO0000000OOOOOOOOOkkkkdoc:coxOOdccllllc;;c;.','''','.",
",codddxxxkkkkkOOOOO00000000000O0OOOOOO00000000OOOOOkOOkxxdlc;;:loxOOdcccloc;;::'.,,,'''''.",
",clodddxxxkkkkkOOOOO0000000000OxodOOOO000000OOOOOkxxkxdlc;,,:ldxkOOxlccll:::c,..,;,,''''.",
".,clooddxxxxkkkkkkkOOOOO0000000kxkOOOOO00000OOOOOOkxdl:,'',,:lxkkOOklccccccl:'..';,,,''..",
".;cooooddxxxxkkkkkkkOOOO000OO0OOOOOOOOO000OOOOOkkdo:,..'''',cxOkxOklccccllc;.',,;;,,'...",
".;codoooddxxxxxkkkkkkOOOOOOOOOOOOOOOOOOOOOOOOkxoc,...',,,;lxOkxxkkoc::ccc:,..,,;;;,''..",
".;cldddooddxxxxxxkkkkkkkkkkOOOOOOOOkkkkkkkkkkkdlc;',:ccldOOkkxdxkdc::clcc,. ..,;;,'...",
"'oxkkOOkkkxooddddl::lddddoooolclodddxxxxxddolllodxxxxxdlodxkkx:..,,;:;;,,...':ol;'..",
"'dkOOOOkxlcclollcclllodddddddxxkkkkkkkkOOOOkkxxdooodxkkkxdddxo,.',,,,;:;...',lo:;,.",
"'dOOOkxol:cododxxdoodxxxxxxkxkkkkkkOOOOOOOOOOkkxxdoxOkxkkxdol:'''';;:::,..'':olcc'",
"'oOOkdoc;;:odddddddxxxkxxkkxxxkkkkkkOOOOOOOOOkkkxdk0kdddxxdol:,',;;;:::'....:lccc.",
".cdxxdc;;:coolooddxxxxkxxxxxxxxxxxxkkOOOOOOOOkkkxk0kddoodddoollc;,'',:;..'..,,,;.",
".;clllllllc;,:oddxxxxxxxxxxxxxxxxkkkOOOOOOOkkkkO0Oxdddool:,',::::;,;'.........",
".';cloolc:;'':odddxxxxxxxxxxxxkkkkkkOOOOOkkkkxk0Oxddoll:,......,;;;,,........",
".:lclooccc:;:oddddddxxxxxxkkkkkkkkkkkkkkkkkxxk0Oxdolc:;'.. .......,;:;'.",
"';:llllooooooddddddddddxxxxkkkkkkkkkkkxxxxxk0Odolc:;,'..       ....,::,.",
"..',:cllcccllllccccccccllllllllcccccc:::clc;,,'.....              .''.",
" ",
" ",
" ",
" ",
" ",
"......                                                                                                                                                                                                       ",
".;,',:,..''..                                                                                                                                                                                                 ",
"'ll:cc;,;:;,.                                                                                                                                                                                                 ",
".,ldoolcc;,'.                                                                                                              ...                                                                                ",
".'lxdolc;;'...                                                                                                        .',,;;,'..                                                                             ",
".';cdxxdol;,;,'''..  .                                                                                               .,lddlcc;'.                                                                              ",
"....;lxkxxdolc:,'..'..'.                                                                                             .:dkkxo:;,'...                                                                            ",
".',''ckkkkxd:,;;;,,;:'...                                                                                        ..,cxkkkkoc:;'..                                                                             ",
".,:cldOOkkkxlllc::lc,''.                                                                                       .';lxOOOOxo:;'....                                                                            ",
"..,;:lk0OOOkxolllll:,,'..                                                                                     .':oxO0OOkxolc;;:;...                                                                          ",
".;;cldO0OOOkxooolcccc;..                                                                                 .. .':oxOOOkkkdoooollc,..                                                                          ",
".';cclx00OOOkxolcllll,.                                                                                  .,,,:lxOOkkkxdoooollc:,...                                                                         ",
"....;lok000OOOxolccllc,..                                                                              ....,:ldkOOkxxxdllcc::,.....                                                                          ",
".,;,;ccdOKK0OOOdlcllc:,.                                                                          ..  .;,',:oxkOOkxxxdlcc::;;,'...                                                                           ",
"..'cc:cclkKKKOOOxollc:,.                                                                           .'.',;;:coxO0Oxdxxdoc:::;;,'....                                                                           ",
".;;,,;clxOKK0OOkxoc:::.                                                                            .,:c;,codkO00kxdxxoc::::;,'..                                                                              ",
".,;,:lodOK0Okkkkoccc,.    ...                                                                      .,:llox0000Oxdxddlc::;,'...                                                                               ",
".'...':looxO00Okkkkxl:'.....'..                                                                   ..   .;lkO000Okxxxxdolc:;;;,..                                                                                ",
".;'..,;:cld000Okkkkd:',:::;..                                                                    ..',,;,:dO00OOkxxxddl:::;;;'....                                          ..........                           ",
"..',,,:cclok0K00OOOkdlcc::,.                                                                 .....':cllloxO00Okkkkxxdc;,;,','.                                           ..',;;::;,'.                            ",
"...                                  ..':c::cllodxOKKK0OOOkxl;',,....                                                               ..'''',;coxkOOOkkkkkkxdl;'','..                                          .';cloooolc,.                              ",
".':c'.                               ..'':c::clxdxOKK000OOkkoc,,,.....                                                                 ......'ckOkkkkkkkkxdc;;;,'......                                   ..':oxxxddlc::::;'.                            ",
".''';lc'.                            ..''';::;;cdxOKK000OOOOkoc:;'.'..                                                                .....',;cdOkxkOOOkkkdl;;:,... ...                                 ..,coxkxxdollcc:::;'..                            ",
"....,::oddc'.                           ....,,,,:clx0KKK0OkOOOxc'.'''.                                                                 ..,,;:looxOOkOOOOOOkxdc,............                             .,cdxkkkxdolcc:::;;,..                              ",
"..,;;:loxxkkl.                            ..':,...:kKKK0OkOOOOxc'...                                                 ..                ..,;cloodkOOO00000Okxo;..'''',,'...                           ..:oxkkkxxdolcc::::;;;..                               ",
".,;;::coxkOOx:.                        .,;::lol::dO000OOO00Okxl;'...              .    ....             ..                       ..'',;clloddxOOO000KK00Okxoc:cc:,...                             .,cxkkkkkxdolllccc::;'....                               ",
".',;;::loxOOOOd;.                      .....';:lxO000OOOO00Okd;....,'.          ....................................           ...'':llloddodk0000KKKK0OOkko:::,..                              .;lxkkkkkkxolllcc:;,'...                                   ",
".';c:cldkOOO0Ol.                      ..''''.,lk0OOO0O000OOx:..  .'..         ......  ............................ ...  ....  ..,;;cclloddk000KKKKK000Okxl:;;,....                          .;okkkOOkkkdolc;,,,''...                                     ",
"..,::::lloxO00K0d'                     ..'',;cldO0OO0000000Oko;....... .   .....,,;:cclloodxxkkkkkkkkkxxxdolccc::;;,'..............';:::cloO000KKKKK00OOkxlcc:;,;;;'.                      .,okkkOOkkkkollc::,'.....                                      ",
".;::llloodk0KKKKKk;.                ....',;:lodk00O0000KKK0OOd;''''''..',:coodxkO00KKKXXXXXXXXXXXKKXXXXXXXXXXKKKK000Okxdolc:;,'.......',;:oO000K00000OOOko::c;,;;;:,.                    ..cxkkkkkkkkxdollc;;::;'..                                       ",
".:llllllloxk0K0KKKk:.             ..'','',;:lodxO000KKKKKK00Od'...,:ldxO0KKKKXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXKKKK000OOkxoc;'.....cO0000000000OOkxdolcc:;'...                   ..:dkkkkkkkkkxollc:::'.''...                                       ",
".';::::cloodO000000Ol.          ..',,;;:clooxkxk0000KKKKKK000kddxO0KXXXXXXNNNNNNWWWWWWWWWWWWNNNNNNNNNNNNNNNNNNNWNNNNNXXXXXXKKK0000Okxolccx0000000000OOkkxdlcc:;,.....                ..cdkkkOOkkOOkdllll::;;;'...                                         ",
".....,:llloodkO000000Od;.       ...''',;coodddxxk00000KKKKKKKKKXXXXNNNNXNNNNNNNWWWWWWWWWWWWWWWWWWNNNNNNNNNNNWWNWWWWWWWNNNNNXXXXXKKKK00000000000000000OOkkdc;;;;::;,'....            .'cdkkOOOOOkOkxdol:;;:::;;'...                                         ",
"....';;::cccloxOOOOO00Okl'.          .;:clloodxxk00000KKKKKKKXNNNNNNNNNNNWWWWNNWWWWWWWWWWWWWWWWNNNNNNNNNWWWNNWWWWWWWWWWWWWNNNNXXNNXXXXXKKKK0000K00000Okkxolccc::::;,'...         ..,lxkkkkOOOkkOkkdoollc:,'.','...                                         ",
"...,,,;:ccccoxkOOOOOOOOkl'.     ...,,,:cloddxxk00KKKKKXXXXNNNNWWWWWWWWWWWWWNNWWWWWWWWWNNNWWWWWWWWWWWWWWWWWNNWWWWWNWWWNNWNNNNNNNNNNNXXXXXKKK00000KK0OOkdc:;;,'.....         ...;cokkkkOOOOOkkkkxdllc::::;,,'....                                          ",
"..'''';:cccccloxkOkkOOOOO0ko;.. ...'',;;::clodk0KXXXKKXXXXNNNNWWWWWWWNNNWWWWNNNNNNWWWWWWNWWWWWWWWWWWWWWWWNNNNNWWWNNNNNNNNNXXXXNNNNNNNXXXXXXXKK000KK000Okdc;,,'.....     ...,:ldxxkkkkkkkOkkkkkxxool;'',;,'.....                                           ",
".,:cccllloxkkkkkOOOO00Oxoc;,'...',;:cdk0KKXKXXXXXNNNNNNNWWWWWNNNNNNNNWNNNNNNNNWWWWWWWWWWWWWWWWNNNNNNNNNWWNXNNNNXXXXNNXXXNXNNNNNNXXXXXXXKKKKKKKK000Okdlc:,......',:codxkkkkxxkkOkkkkkkkxxxdoolc;;,,;;'.                                              ",
"...,;,,;;:clodxkkkkkkOO000KKKK00OkOOO00KKKKKXXXXXNNNNWWWWWWWWWNNNNWNNNNNNXXXXXNNWNNNWWWWWWWNWWWWNNNNNNNNNNNNNXXXXNXXNNNXNNNNNNXXNNNNXXXXXXXKKKKKKKKKK000Okxdooooddxxkkkkkkkkkkkkkkkkxxkxxxdolccc:,,;;;,''.                                             ",
"..'',:c;,,;:clllodxxxkkOO0KKKKKKKKKXKKKKKKKXXXXXXXNNNWWWWWWWWNWWNNNNNNXXNNNNNNNNNNNNNNNNWWWWNNNNNNNNNNNNNNNNWWWNNNXXXXNNNNNNNNNNNNNNNNNNXXXXXXKKKKKKKKKKKK00Okkkkkxxkkkkkkkkkkkkkxxxxxkxxolol::c:;;'...';'..                                             ",
"...                          .........,;:;,;clodxxkkOO0KKKXXKKKKXXXKXXXXXNNNNNWWWWWWWWWNNXXXXNNNNNXXXXXXNNNWWNNNNNNNNNNNNNNNNNNNNNNXNNNNWWWNNNXXXXXXXXXNNNNNNNNNNNNNXXXXXXKKKKKKK00KKKKK0OOOOkkkkkkOOOOkkkkxxxxxxxxdol,,c:,::;:;'. ....                                              ",
"....,;'.                        ......'',;..',:cccldxxxkOO00KKKKKXXXXXXNNNNNNNWWWWNWWWWNNXKKKKXXNNNNNNNXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXNNNNNXXK00KXNXXXNNXXXXKKKXXNNNXKKKXXXKKKK0000KKK00OOOkkOOOOOOOkkkxxxxxxdddllll:;;;',;::,'...                                                 ",
"..'',:clll:'.. .                    ..'....,'.;:c:;;cccoxxxkkOO0KKKXXNNNNNNNWWWWWWNNNWWNXKOdoxOO0KXNNNNNNNNXXXXNNXXXXXXNNNNNNNNNNXXXNNNNNNNNNXXXXXXXXKKKXXNNXXXXXKK0Okdodk0XXXKXXXXXKK0000000000OOkxkkkkkkkxxxxxdxdddlcolc:cc::,'.,;.  ....                                                ",
".;cclooddddddlclc:;,....                  .::::;,';cllllcldxkkOO00KXXNNNNNNNWWWWWWWWWWWXkoc:coxkk0XXXNNXXKKKKXXXKKXKKKXXXNNNNNNNNNNNNNNNNNNNXK0KKKKXK00KXXXXXXXXXKKOxl;,,cokKXXXXXXXKK0000000OOOOOxdddxddxxxxxxxdoolll::ccc::::;'.,,.                                                      ",
".';:loodxxxkkkOkkOOOkkdoc:,'.            .,,.';,.,cccc:,,:odxxkkO0KXXXXXNNNNNWWWWWWWWWKx;'',okxdk0XXXXNXXXXKKKXXXXXKKKXXXXNNNNNNNXNNNNNNNNNNNXKKXKKKKK0KKKXXXXXXXK0xo:'...,lk0XNXXXXKKK00000OOOkkkkdooddddddddddolll:;:::::::;,,'...                                                       ",
"..',::;:cclllodddxkkOO00000Oxl:'..  ..  .....;;,;:c:::;:cloooddxO0KXXKXXXNNNNNNWWWMWWXx;..''okdd0XNXNNNNNNXXXXXKXXKKKXKKKXXXNNXXXNNNNNWWNNXXNNKKXXXKKXKKXXNNXKKKXX0xl;'....,lkKNNXXXKKKK000OOkkkkkkxddoddooolcclll:cc;'..,;;,'....                        .....                            ",
".......',.,;,;codddxkkOO00000Oxdccl;..   .,,.,c:cc:;,;clooodxO0KXKXXXXNNNNWWWWWWWWN0dc..':lod0NWNNNNNNNNNNNNXKKXXKKKKKKKKXNNNNNNNNWWWWNXKKXNXKXNXXXXXXXNNNNXXXNNXOdc;'...';d0KXXXXXKK00000OOkkkkxxxxxxdlclc;,;:c::c:;,...'''..... .........',,;;;;,,'',,,,,'.....                        ",
"......':lllooddxxkOO000000K0Oxdl:;;:,',:c:,'',codxkkOKKKKXXXXXXNNWWWMWMMWWWWOl:;,;cokKNNWWWNNWNNNNNNXXXXXXXKXXXXNNNNNNNNNWNNNNNNNXXNXKKXXXKKXXXNNNNNNNNNXK0kxol;'',:dO0KXXNNXXK00000OOkkkkkxxxkkxxxdlc:cccclc;,;:::ccc:cllooooodddxxxxkkkkkkxxxdolccc:;;;'...                     ",
"....;cccclloodxxxkkO00000000000OOkxxkkdodkkkO0KKKK0KKXXXNNNNWWWWWWWWNNWWWXkllodxOKXXKXXXNNNWNNNNNNNNNNNNNNWNXXNNNNNNNWWWNXXXXNNNXXXXKKKXXNNNNNNNNNNNX000OkxxdoooxO00KXXXXXXXKKK00OOkkkxkxxxxkkkkkkkkkkkOOOOkkkkkOOOO000000OOOOkkkkkkkkkkkkkxxxxxxxdolc:;,,.                    ",
".:c:;:c:clllodxxxkkOO0000KK000000000000KKKKKKK00KKKXXNNNWWWWWWWNXXNWWWWNXK000KKXKKKKNNWWWWWWWWWWWNNNNNWWNNXXNNNWWWWWWWNNXNNNNNNNXXXNNNNNNNNNNNNNXK0000OxxdxkkOO0000KKXXXXKKK000OkkkxxxddxxxkkkkkkkOOOOO0000OOOO00000OOOOOOkkkkOkkkxxxdddooooloddddollc;,,'..                ",
"...';,':cccccloddxxxkkOO00000000000000KKKKKKK000KXXXNNNWWWWNNNNNNNNNNXXXXXXKKXXXXXKXNWWWWWWWWWWWWWWWNNWWWWNNNNWWWWWWWWWWNNNNNWWWNNNNWWWWWWWNNNNNXKKKK0OOOO0O0000000000KXXKK00OOOOkkxxxddddxxkkkOOOOOOOOOOOOOOOOOOkkkkkOOOkkkxxxdddoloolcc,,:;,::::::::;:c:,.                ",
"..';::ccc:cccloddxxkkkkOOO00000KK0000K0000000KXXXNNNNNNNNXXNNNNNNNNNNNXNWNNNNNNNNWWWWWWMMWWWWWWWWNNWWWWWWWWWWWWWWWWWWWWWWWWNNNNNNWWWWWWNNNNNNNXKKKK0KKXXKKKKXXKKK000KKKK00OOOOkkxxxdodddxxxkkkkkOOOOOkkkkkkkkkkkkkkkkxdddooolllc;:c:,;,..,'.',..........                 ",
"..;;:ccc;',::clllodxxkkkkkOOO000000000000OO0KXNNNXXNNNNNNNNNNNNWWWWWWWWWWWWWWNWWWWWWWMMWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWNNNNNNNNNNNXXXXXKKKKKXKKXXXXKKKKKK00000OOOOOkkkxdoodddddxxxxxkkkkkkkkkkkkxxxxxdoooolllcccc;;cc:;;'... ......... .                     ",
".;,',,.';;:ll;;cllodxxxxkkkkkkOkkOOOOOOOO0KXNNXXNNNNNNNNNWWWWWWWWWWWWWWWWWWWWWWWWWMMMWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWNNNNNNNNXXXKKXKKKKKKKKKXXKKKKKKK0000000OOkkOkkkkxooooooooddddxxxxxxxxxxxxxdoclolllclcc:;;cc,.,;,'....   ..                             ",
"... .',,,,:c'':ccccodooodxxxkxxkkxkkkkkkkOKXNNXNNNNNNNNNNWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWNNNNNXXXXXXXXXKKKK0KKKKKKKKKKKK0000000OOOOOkkkkkkxxdollllllooooddddddddooolcloc;:c::::;;::;,::,..'..                                      ",
".....':;,cc:;:cllcc;cdoodddxxxxxxxxxxk0KXNNNNNNNNNWNWWWWWWWWWWWWWNNWWWWWWWWNNNNNNNNNNNNNNNNNNNNNNNWWWWWWWWWWWWWWWWWNNNNNXXXXXXXKKKKKKK000000000000000000000OOOOOOkkkkkkkkxxolllllllllllollllclllcc:;cl;.;:;;'.,'';:;;;,...                                        ",
".,:cc;'',:clc:::llccloclddoodddddxOKXXNNNNWWNWWWWWWWWWWWWWNNNNNWWWWWWWNNNNXXXXKKKK000000KKKKKKKKXXXXXXXXXXXXXXXKKKKKK0000000000000000000OOOOO00000000OOOOOOkkkkkkkkxxdolcclcccccccclc:cc:cc;;c::cc'.,:;;'....''......                                         ",
".','..';::;;c:;:ll;'clclol;;loolodx0KXNNNWWWWWWWNNWNNNNNNNNNNWWWWWWWWWNNNXXXXXKKKK0000000000000KKKKKKKKKKKKK00000000000OOOOOOOOOOO000000OOOkOOOOOOOOOOOOkkkkkkkkkxxxdolc::cc:,;:;;cc;;::;cc,;:c;;:'.,'....   ..                                               ",
"... .,;,'.....'::;':lcclclc;:clcloox0KXXNNNWWWWNNNNNNNXXXXNNWWNNNNNNNNXXXXKKKKKKK00000000000000000000000000000000OOOOOOOOOOOOOOOOOOOOOOOOOkkkkkkkkkkkkkkkkkkkkkkxxxdocc:,,::;,,:,,;',;:::cc;;;'..:;...                                                        ",
"...    ..;;...;:,,cc;:c::clcclclk0KXXNNNNNNNNNNNXXXKKKXXXXXXXXXXKKKKK000000000OOOOO000OOO00000000OOOOOOOOOOOkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkxxxxxxkxxxdl;:c:'';,'..;,,,.';:,,::'... ...                                                           ",
"..,,...',,',c:..;cc:cl:cl::lk00KXXXXXXXXXXKKKK000000KK00000OOOOOOOOOOOOOkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxkkkxxxxxxxxxxxxxdo;.;;,'';,...';,'..;,.....  . .                                                             ",
".....',.. .;'..';::;clcc:'.'lxOKKXKKKKKKKKKKK0000OOOOOOOOOkkkkkkkkkkkkkxxxxxxxxxxxxxxxxxxxxxxxxxxxxxddddddxddddddddxxxddddddddddddxxxxxxxxxxxxxxxxxxxxxdoc'.;'.'.';,.....',,'..  .                                                                   ",
"...    ..  .',,..:cc:'.,;,;oO00KKKKK00K000000OOOOOkkkkkkkkxxxxxxxxxxxddddddxxxdddddddddddddddddddddddddddddoooodddddddddddddddddddddddxxxxxxxxxxxxxol:;'.,'....,,'..  ..,..                                                                       ",
".... .,;,.......'lxkO00O00000OOOOOOOkkkkkkxxxxxxxxxxxddddddddddddddddddddddddddddddddddddddddoooooooooooooooooooooooddddddddddddddddddlc;';;',,.  .......    ...                                                                       ",
"...     ..,:;;cdxkkkkkkkkkkkkkxxxxxxxxxxxxddddddddddddddddddddddddddoooooooooooooooooodoooooooooooooooooooooooooooooooodddddool:'.'.,,...'.    ...                                                                               ",
".'......,:clodddxxxxxxxxxxxxxddddddddddddddddddddooooddoooooooooooooooooooooooooooooooooooooooooooooollooolllooolcc:;'.......,.  ....                                                                                    ",
"..    .  .....'',;:codddddddddddddoooooooooooooooooooooooooollllllllllllllllllllllllllllllllllllllllllllllllcc;,......'.    ..'.  ...                                                                                    ",
".. .....  ...;coooooooooooooooooollllllllllllllllllllllllccccccccccccccccccccccccccccccccccccccccc:,'..       ..      ..                                                                                         ",
"..  ............,cooooooooolllllllllllllllllllllcccccccccccccccccccccccccccccccccccccccccccccccc:,...       .                                                                                                     ",
"...............cdxxddooooolllllllllllcccccccccccccccc::::::::::::::::::::::::::::cccccccclllooc'                                                                                                                ",
"..................:dkkkxxddooooollllllcccccccccccc::::::::::::::::::::::::::::::::::::cccclllooodoo:.  .                                                                                                            ",
"....................;dkOkkkkxxddoooolllllccccccc::::::::::;;;;;;;;;;;;;;;;;;;;::::::::ccccllllooooooddl,                                                                                                               ",
"...................;lxOOOOOkkkxxxddoooollllccccc::::::::;;;;;;;;;;;;;;;;;;;;;;;;:::::ccccllllloooooodddoc.                                                                                                              ",
".   .  . .........,:lxO0000000OOkkxxxdddooolllccccc::::::;;;;;;,,,,,,,,,;;;;;;;;;;::::::cccccclllloooooddddl'.                                                                                                             ",
"..          ..  ..  ..........':lxkO0KKKKKKKKK0OOkkxxdddoooolllcccc:::::;;;;;;,,,,,,,,,,,,,;;;;;;;::::::::cccccllllloooddddd:..  .   .                                                                                                     ",
".     ...   .. .....';coxk0KKKXXXXXXXXKK000Okkxxdddooollllccccc:::::;;;;;;,,,,,,,,,,,,,;;;;;;;;::::::::cccclllllooodddddl,.                                                                                                           ",
"...   ..,:loxk00KKXNNNNXXXXXXXXKK00OOkkxxdddooollllccccc:::::;;;;;;,,,,,,,,,,,,,,;;;;;;;;;;;:::::cccclllloooodddxdo:.                                                                                                          ",
".. ..';ldkO00KKXXNNNNNNNNXXXXXKK000OOkkxxxddooollllccccc::::;;;;;;;,,,,,,,,,,,,,,,;;;;;;;;;;;;:::::cccllllloooddxxxddl,.                                                                                                        ",
"...,coxk0KKXXXXNNNWWWNNNNXXXXXKK0OOkkkxxddddooollllccc::::::;;;;;;;,,,,,,,,,,,,,,,,,,,,,,,;;;;;;;::::ccclllloooodxxxxxxo:.                                                                                                       ",
".  .':oxkO0KXXXNNNNWWWNNNNXXXXKKK00Okkxxddddoooollllccccc:::::;;;;;;,,,,,,,,,''''''',,,,,,,,,,,,,,;;;;;:::ccclllooodddxxxxxxdl;..                                                                                                    ",
".,cxkOO0KXXXNNNNNNNNNNXXXKKK00OOkkxddoc:lddlllllcccc::::::;;;;;;,,,,,,,'''''''''''''''''''''',,,,,,;;;;::::cclllooodddxxxxxxxoc,.                                                                                                   ",
".'lxkO00KXXXNNNNNNXXXXXXKK000Okxxdl:;;,....codoooollccc::::;;;;;,,,,,,'''''''............'''''''',,,,,,;;;;:::cccllloooddxxxkkxxdo:'.                                                                                                 ",
"..:dkOO0KKKXXXXNXXXXXXXXKK00Okxxdoc,.  .  . ..;cooooollccc:::;;;;,,,,,'''.......................'''''',,,;;;;::::::cclloooddxxkkkkkxdl;.                                                                                                ",
".:xkOO0KKKXXXXXXXXXKKKKK0Okkxdl:,..   .. .... ..,cllllccc:::;;;,,,,''''..........................''''',,,,;;;;;::::::ccllooddxxxkkkkxxdc,.                                                                                              ",
".;dkO00KKXXXXXXXXKKKK000Okxdl:,..      .  .. ..  ..';ccc:::;;;,,,,'''...............................'''',,,,,;;;;::::::cclloodddxxkkkkkxxdl;'.                                                                                           ",
".lkO0KKKXXXXXXXXKKK0OOOkdo:'..           ........ ....';;:::;;,,,'''..................................'''''',,;;;;::ccc::cllooodddxxkkkkxxxdo:'.                                                                                         ",
"'dk0KKXXXXXXNNXXK00Okxdl;..               ....... ........',,,,,'''''..................................'''''',,;;;:cclolc:cllooodddxxkkkkxxxddo:..                                                                                       ",
".:xOOKKXXXXXXXXKK0kkdl;'..      .          ....... .... ..  ...';;;;,,''''...............................'''',,,;;::cllooolcccloodddxxxkkkxxxxxddl'                                                                                       ",
".lkO0KKXXXXXXKK0Okxo:.....     ..   .. ........... ...........':loddoll::;,,''...........................''',,,;;:::cclllooolcclooddxxxkkkkxxxxxddl;.                                                                                     ",
"'okO0KXXXXXXKKK0Oxo;...             .....    ...  ..........';coddxxxxddoolc:;,,'''''''''''''''......'''',,,,;;;::::ccccllooolcclodddxxxkkkkxxxxxxdo;.                                                                                    ",
".,dO0KXXNNNXXKK0Okd;....                       ......... ...,clddxxxxxxddddoollcc:;;;,,,,,,,,,,,,,,,,,,,,,,,,;;;;;;;::::cccllooolllooddxxkkkkkkxkkxxdo,.                                                                                   ",
".:xO0KXNNNNXXKK0kxd,....                       ...........,:lodxxxxxxddddooolllcccc::::;;,'''''....'',,;;,,,;;;,,,,'',,;:::ccloooolllddxxkOkkkkkkxkxxdl'                                                                                   ",
".ckOKXXNNNNXXK0Okxo,.. .       ...             .........,:lodxxxxxxddddooolc:;'''''''''...............'',,;;;;,,'.......',;::cllloooooodxkOkkOkkkkkkxxd;.                                                                                  ",
".lk0KXNNNNXXKK0Okdo;. .                ..       ... ..':lodxxxxxxxddooollc:;'..........      ............',,,,'...  ......',;::cllooododxkOOOOOkkOOkkxd:.                                                                                  ",
".ok0KXNNNNXXK00Okdo;. .                ...    .. ....;coddxxxxxxddooollc:,.... .....         ..   .    .........    ..   ....,;::cloooodxkkOOOOOOOOkkxdc.                                                                                  ",
",dO0XXNNNXXXKK0kxdo:. .                ........ ...,:lddxxxxxxxddooolc:;'..                            .   .                ...',;:clloodxkOOOOOO0OOkxoc..                                                                                 ",
".;kOKXXNXNNXXXK0Oxxdc.  .               .......  .':loddxxxxxddddooll:;'..  .                                                   ...,;:clodxkOO00000OOkxoc;'.                                                                                ",
".ok0KXXNXXXXXXK0Okxdc.. ...                .   ..,coddddxxxddddoolc:,...                                                          ...,;codxkOO000K00Okxolll;'.                                                                              ",
".:xO0XXXXXXKXXK0Okxddl'.                ..... ...;coddddddddddooll:,.....                                                            ..'codxkOO000K00Okdolodoc;..                                                                            ",
".,dO0XXXXXXXKKKK00Oxxdo;. .....   ..   ...... ..,:lodxxxxxddddool:,....                                                                 'lodxkOO000000Okdoodddolc,..                                                                          ",
".    'ok0KXXXXXXKK0OOOOkkxxdl'......  .     ........,coddxxxxxxdddolc;'.. ..                                                                .;odxkkOO000000Okdoodddddol:,..                                                                        ",
".;dO0KXXXXXXXXKOkkOkkkkkxxo;... .         .....';lodxxxxxxxddool:'.....                                                                  'lodxkkOO000000Okdooddddddooc:,..                                                                      ",
".,lxO0KXXXXXKKXXK0OOkkOO00Okxxoc;'.......     ..,:oddxxxxxddddolc;....                                                                    .codxxkOOOO00000Okdoooodddddoolc:,..                                                                    ",
"..'lxO00KXXNXXXXKKXKK00OkOOO0K0Okxxddolcc::,... ..;codxxxxxxdddoolc;.. ..                                                                   .codxkkkOOOO0000Okxdlllooddddddoolc;'..                                                                  ",
".,lxO0KKKKXNXXXXXXXXXKK0OkkkkO0OOkkkxdl:;;:::;'...:lddxxxxxxddooolc:'....                                                                   .:oddxkkOOOOOOOOOOkxollllooddddddooolc;'.                                                                 ",
".'lxO0KK00KXXXXKK00KXXXXK0OkdlccodxO0OOxo;..... ..,codxxxxxxxxdoollc:'..                                                                     .;odxxkkOOOOOOOOOOkkdoccclloodddddoooolc:,..                                                               ",
".:dkO0000OKXXXK0Okxk0KXXXK0Ox:.....':ldxkkxl,. ...;lodxxxxxxxxdooolc:'.                                                          ...         .,loxkkOOO0OOOOOOOOkkxoc::cllloooododddoolc;'..                                                             ",
".'cdkOOOkxxOKKKKKOxl:cdOKKK000kc.  .......';:col' ..;codxxxxxxxdddoolc;'..                                                                     .,ldxkOOO00000OOkkOOkkxdl:::cclloooooodddoolc:,..                                                            ",
".'cxO00Oxl:lOKKKK0kc....;xO00O0Od,. ...   .    .....';lodxxkkkxxxddoolc;'...                                                                    .,oxOOOOO0000000OkkOOkkxxdlc:::clllloooodddoollc;'..                                                          ",
".'cdk0Oxo:..cOKXXKOd,......:kOOOOkc.               ..':lodxxxkkxxxddoll:,...                                                                   ..,lxkOOOOO00000K00OOOOOOkxxxxdlc:::cclllooooooooolc:,..                                                         ",
".:oxkxl,.. .lO0KK0kc........;x000Od'               ..':lodxxxxxxxxddool:,....                                                                .':oxkOOOOOOkkOO00KK00OOOOOOOkkxkxxdlc:::ccllloooooooollc;'..                                                       ",
".,lxxl;..   .lO000Od,...  .. .ckO0Ox:.              ..,:ldddxxxxxxxdddolc;'....                                                               .:dxkxxddoc::ldxO00KK00OkkOOOOOkxxxxxxdlc::cclllloooooooolc:,..                                                      ",
".,odl,.    .,d0KKKx:..... ... .lOOkxc.             ..';clodxxxxxxxxdddoolc,.. ..                                                               ..'''.....   .;dkO0K00OkxxkOOOOkxdodddxxdl::ccclllllloooollc:;'.                                                     ",
"'lc'.     .ck00Kkc..  ....... .oOkx:.            ...,:lodddxxxxxxxdddooll:,..                                                                                .:xO000OkxddxkOOOOkxc,;codxkdlc:cccclllllllllllc;'..                                                   ",
"...     .,dOOOkl.       .. .. ,dko,.           ...';clodddxxxxxxxdddooolc:'.                                                                                  'okO00OkxolldkO00Oko,..,:loxxdlcccccccllllllllll:,..                                                  ",
".;dkkd:..         ..   ,xx;.          ...,;clooddddxddddddddooollc;'.                                                                                  .:xO00Oxc....;okO0Oko'..',:codxoc:cccccccllllllllc;'..                                                ",
",dxc'.                 .,'.         ..';:clooodddddddddddddooooll:,..                                                                                   .oO0Oxc.     .;okO0Oo,..',;:lddlc:ccccccclllllllllc;,...                                             ",
".''.                              ..',:cllloodddxxddddddddooooool:,.. .                                                            ......                ,d0Ol.        .:dO0Od,..';;:codl:::::::ccllllllllllc:;'...                                          ",
"....';:clllooddddddddddddddoooooooc;'.                                                             .......                .cxl.           .cxOOd,.',;::clc:::::::::cclllllllllllc:,'...                                       ",
"..';:cloooodddddddddddddddooooooolc;.. .                                                         .........                ...             .'okOo'.,;::;;::::::;;;::cccccclllllllllc;,...                                     ",
"...';ccloddddddddddooooddddoollllooll:'. .                                                        ............                                .:xd;',;::;;;;::::;;;;;:::ccccccclllllllc:;,'..                                  ",
"...';cloooooooooooooooloooddoollcccllll:'. .                                                         ...........                                 .;c,',:::;,,;;::;;,,,,;:::cccccc::::cclllllc:,...                               ",
"..,;:lloolcccclooooooolllloooolc:,.';clc:'.                                                                                                          ..,:::,'',;;;;;,'',,;::cclllc:;,''',;:cccc::,..                              ",
"..,;clllcc:;,,;clodddol:;:clooolc;.. ..,::;'.                                                                                                           .,;:;'..',;::;;,'''',;:clllllc;,......'',;::,'.                             ",
"..';:clc:;,'..',cloddol:,..;cooooc;..   .......                                                                                                           .';:,....';:c::,'......,;:lllllc:,..    ...'''..                            ",
"..,;:c:;'.....';cloddoc;...':lddol;'.                                                                                                                      ..,,..   .';:cc;'.      ..,;cloool:,..     ....                             ",
"..,;:;,...  ..':cloool:,....;loddl:'.                                                                                                                        ....     .';cc:,..        ..';:clc:,.                                      ",
"..',,'...   ..;clooolc;..  .':odol:'.                                                                                                                                   .';::;'.           ..';:c;'.                                     ",
"........    .';cloolc;'..  ..,cool:,.                                                                                                                                     ..,;:,..            ..,;;,..                                    ",
"......     .';clll:;'....  .':lolc,.                                                                                                                                       ..',,'.             ...''..                                    ",
"...;ccc:,....... ..,cll:,.                                                                                                                                         ...'..              .....                                     ",
"...,:c:,...       ..,:c:'.                                                                                                                                           .....                                                        ",
"...,;;,..  ..   .....,;,'.                                                                                                                                                                                                         ",
".........................  .                                                                                                                                                                                                      ",
".......................                                                                                                                                                                                                         ",
".... ....................   .                                                                                                                                                                                                     ",
"... .......................                                                                                                                                                                                                     ",
"...................                                   .                             ..                                                                                                                                 ",
"....................                             .                                                                                                                                                                ",
"........................                            .                                                                                                                                                                ",
".......................                      .                                                                                                                                                                     ",
".    ........................                                                                                                                                                                                        ",
"..........................                                                                                                                                                                                     ",
"........................                                                                                                                                                                                       ",
".. ...................                                                                                                                                                                                        ",
"...................           ..                                                                                                                                                                          ",
"...................                                                                                                                                                                                       ",
".................                                                                                                                                                                                        ",
"...............                                                                                                                                                                                        ",
".................                                                                                                                                                                                      ",
".................                                                                                                                                                                                     ",
"..................                                                                                                                                                                                   ",
"..................                                                                                                                                                                                  ",
"...............                                                                                                                                                                                    ",
"............                                                                                                                                                                                    ",
".. .......                                                                                                                                                                                    ",
"......                                                                                                                                                                                    ",
".........                                                                                                                                                                                 ",
".......                                                                                                                                                                                 ",
".....                                                                                                                                                                                 ",
"...                                                                                                                                                                                  ",
".                                                                                                                                                                             ",
"...                                                                                                                                                                            ",
" ",
" ",
" ",
" ",
" ",
" ",
"..........','.                                                                                                                                                                                                                                                            ",
"..........,,'..                                                                                                                                                                                                                                                          ",
"...... ...',,'.                                                                                                                                                                                                                                                         ",
"....... ...',,,'.                                                                                                                                                                                                                                                       ",
"....... ...';;;;'.                                                                                                                                                                                                                                                     ",
"......  ...',;;;;'.                                                                                                                                                                                                                                                   ",
"...........',;;::;,..                                                                                                                                                                                                                                                ",
"...........',;;:::;'.                                                                                                                                                                                                                                               ",
"............',,;;:::,.                                                                                                                                                                                                                                              ",
"............',;;::::;'.                                                                                                                                                                                                                                            ",
"............';::::::;,.                                                                                                                                                                                                                                           ",
"............',;;;::;;;,..                                                                                                                                                                                                                                         ",
".............'',;;:;;;;,'..                                                                                                                                                                                                                                       ",
"..............',;;;;:;;,,'.                                                                                                                                                                                                                                      ",
"...............',;::::;;,,,'.                                                                                                                                                                                                                                    ",
"..............',;:ccc::;;;,'..                                                                                                                                                                                                                                  ",
"...............',:clllccc:;;,,'..                                                                                                                                           .........                                                                           ",
"................',:looooolc::;;,'.....                                                                                                                                  ...',,'''................                                                               ",
".............'''';cooodxxdoolc:::;;;,'..                                                                                                                             ..',,,'.......................                                                            ",
"............''''',:odxxkkkkxxdoooollc:;,...                                                                                                                        ..'''........................'...                                                           ",
"............'''''.';lxkkkkkkkkkkkkkxddolc::;,'....                                                                                                            ................   ...............'''...                                                          ",
"..................'''''',:dkkkkkkkkkkkkkkkkkxxddoc::;;,''........                                                                                                ..,,''......           ..............''...                                                          ",
"....................''''''';oxkkOOOOOkkkkkkkkkkkkkxddollc::;;;,,,'''...                                                                                          ..,,'......             ....................                                                          ",
".....................'''''''',,,,;lxOOOOOOOkkkkkkkkkkkkkkkkxxxdollcc::::;;,'''....                                                                                  ..','......            ........................                                                          ",
".....................'''''''''',,,,,;lkOOOOOOkkkkkkkkkkkkkkkkkkkkkkxxdolllcc:;;;,,,''...                                                                             .',,,.....                 .....................                                                           ",
"....  ............'''''''''',,,,;::cokOOOOkkkkkkkkkkkkkkOOkkkkkkkkkkxxdooolc::::;;;,,'''.......                                                                 ...',,'....                     ...............'....                                                           ",
"................'',,,,,,,,,;;::clodkkOOOkkkkkkkkkkkkkkkkkkkkxkkkkkkkxxddddolllc:::;;;,,,,,,''.......                                                        .';:;;,'.....                       .............'''...                                                           ",
"..............''',;;:;;;;;;::clodxkOOOOOOOOOOOOOOOOkkkkxxdddddxkkkkkkkxkkkkxxxxdoolllllllc:;,,,'''''.......                                              ..;:cc;,'.....                         ............''''..                                                            ",
"....''''''''''',,,;:::::::::ccldkkkOOOOOOOOOOOOOOOOkxddollooxkkkkkkkkkkkkkkkkkkkkkkkkkkkkxdlc::;;;,,,,,''''''''.............                         ...,:clc:,'.....                         .............''''...                                                            ",
"......''''''',,,,,,;;:::ccccccccldxkkkOOOO000K00OOOkkdllooodxkkOOOOOOOkkkkOOOOOOOkkkkkkkkkkkkxdoolc:;;;;;;;;::::::;;;,,,,,,,,,,'...               ...',:clllc;,'......                         .............',,,'..                                                             ",
".........''',,,,,,,,,,;;;;:cclolloodxkkkOOOO000KK00OkxdollldxxkOOOO000OOOkkOOOOOOOOOkkkkkkkkkkkkkkkkkxl:;;;:cloooodolccccclllllloollc:;,'''''''',,,;;:lodddol:;'..........                      .............'',,,,'.                                                              ",
"..........''',,,,,,,,,,,,,;;:clooodxkkkOOOO00KKKKK0OOkdollodkkOOO0KKKK0OOOOOOOOOOOOOkkkkOOOkkkkkkkkkkkxl:;;:ldxkkkkkxdddddxxxkkkkkkkkxxdddddxxdxxxxxxxkkOOxo:,'................                   ...........'',;;,'.                                                               ",
"........'''',,,,,,,,,,,,,,;;::looxkkkOOO000KKKKKK0OOkxddxkkOOO00XNNX00OOOOOOOOOOOOkkkkOOOOkkkkkkkkkkxl:;;:cdkkkkkkkkkkkkkkkkkkkkkkkkOOOOOOOOOOOOOOOOOOOkoc,'....................                  .........'',,,,'.                                                                ",
"........',,,,,,,,,,,,,,,,,;;;:clodkkOO000KKKKKKKK0OOOkkkkkOOO00KNNXK0OOOOOOOOOOkkkkkkOOOOOkkkkxdddddl:;;:cdkOkkkkkkkkkkkkkkkkkkkkkkOOOO0000KK0000000Odl:,''.................    .                     .....',,,,'.                                                                 ",
"........',,,,,,,,,,,,,,,;;;;;:ccldkOO0000XNXKKKK00OOkkOOOOOO0KKKKK0OOOOOOOOkkkkkkkkOOOOOOkkkkdlcllc:;;:cdkOOOkkkkkkkkkkkkkkkkkkkkkkkOOO000KKK00OOkko;,''.....................      ..                ....'',,'..                                                                  ",
"........''',,;;,,,,,,;;;;::;;;::coxOO00O0KXXXKKK00OOOOOOOOO00KKKK000OOOOOOOOkkkkOOOOOOOOOOkxdlc:ccc::cldk0K0OkkxxkkkkkkkkkkkkkkkkkkOOOOO000K0Oxoc:;,'.........................     ......             ...''''..                                                                   ",
".........''',,;,,,,,,,;;;::::;;;:ldkOOOOO00KKKK000OOOOOOOOO000KXXK00OOOOOOOkkkkOO00OOOOOkkdlcc::ccclodkO0KXKOOkxxkkkkkkkkkkkkkkkOOOOOOOO0000ko:,'............................  ..    .....            ........                                                                    ",
".........'''',,,,,,,,,,;;:::::::::cldkkxkkOO000OOOOOOOOOOOOOO0KNNXK0OOOOOOOkkkkkO000OOOOkkdoc:::ccldxkOO0KXXK0OOkkkkkkkkkkkkkkOOOOOOOkkOOOOkdl:,'.............................   ...    .....          ......                                                                      ",
"...........''',,,,;,,,,,,,;;::::::cc::coxkxkkOOOOOOOOOOOOOOOOOO0KNWNK0OOOOOOkkkkkkkOOOOOkkkkxdolc:ccoxkkkO0KXXXK0OOOkkkkkkkkkkkOOOOOOOOkkkkOOxl;,''''.......'''...................           ....          ....                                                                       ",
"...............'',,,,;;;;;;;;;;;:::ccloolccldxkkkOOOOOOOOOOOOOOOOO0XWWWX0OOOOOOOkkkkkkkkkkxxxxkkkkkxdllldkkOO00KKKK000OOOOkkkkkkkkOOOOOOOkkkkxxdo:,'..'..................................                      ...                                                                        ",
".....'''',,,''..'',,,;;:::::::::;;;;ccldxolcllodoxkOOOO00KKKXXXKK00KNWWNKOkkkkOOOOkkxdxxkkxooooxkkkkkkxddxkOOO0KXK00OOOOOOOkkkkkkkkkkkkkkkkkkxoc:;,'...........'''.........................                      .                                                                         ",
"......',,,;;;;;;;,'''',,;;::cccccccc:,,;:clooocccclllokO0KXNWWWWWWNXKKKXNX00OkkxkkOOOOOOxdodxkxollcldkOOOOOOkOOOOO0KK00OOOOOOOkkkkkkkkkkkkkkkkkkkdl:,,'''.........'''''''''''.....................                                                                                             ",
"....'',,;;;::::;;;;,,',,;;;:cllooollc:,,,;ccllcccclodddkO0XNWMMMMMWX00XNXKOOkkkkkkO0000OOkdodkkkxolcclxOOOOOOOOOOOOO00OOkkkkOkkkkxxxxkkkkkkkkkkkkkdc;,,,'''''...'''''..''''''''''....................                                                                                           ",
".....',,;;;;::::::::::;;,,,,,;::clodddol:;,,,;:cccccldxkkkOOO00KNWMMMMWK0KNNK0OkkkOOOO0KKK0OOkdodxkkkkxocclxOOOOO00OOkkkOOOkxkxxxdddddooxkkkkkkkkkkkkkdlc:;,,,,'''''''''''''''''''''''....................                                                                                          ",
"...',,;;::::::::::::ccc::;,,,;::cccldkkdl:;;;:cclllclokOOxxOOOOOKNWMMWNXKKXNX0OOOOO0000KK000OOkdooodxkOOxolldkkkkkkkkxdodkkdoodooollclloodxxxxkkkkkkkkkxolc:;;,,,''''',,,,,,,''''''''''''....................                                                                                        ",
"..,;;:::cccc:::::::::cllc:;;;;:cccccloolc::cloddolccclxkxoxO000KNWMMMNXNNNXK0OOOO00KKKKK0OOkkxxolccclx00Okkkkxdlclllllcclllcclollllcccloolooodkkkkkkkkxdolc:;;,,,,,,,,,,,,,'',,,,,'''''''''''''...............                                                                                       ",
"..,;::::ccccccc:::::::;:clc;;::cccc:;::::::coxkOkocc:::loodk0XXXXNWMMMMWWNXKKK0OO0000KXXX0Okxllllc:::cdO0000OOkdl::::cc::::;:colcccc::ccccccloxkkkkkkkkxdolc::::;;,,,,,,,,,''',,'''''''''''',,'''..............                                                                                       ",
"...,;:::::cccccllcc::cc:;;;ccc::ccccc:,,,;;:coxkOOkoc;;;::lxOKNWWNKKNMMMMMNX000K0OO0000KNWNKOko:;:c:;,;:cx0KKKK0Oxoc:::::;;;;,;cllcccc:;:c:::clodxxxddxxkkxdolccc:;;,,,,,,,,,,,,''''''''''''''''................                                                                                        ",
"..',;;:::ccclllcclllccc:c:;;;:clcccc::;,'',;:lxkO00dc;,,;:cdk0NWMMWWWWMMMMWXK0OOOOOOOOO0KXWNKkdc;;;:;,',;:dOKKXK0Oxolc:::;;;;,,,:ccccc:;;:::::ccloooooooxxxdoollc::;;;;;,,,,,,,,,,,,,,,'''''''''...............                                                                                          ",
"....,,;;::cccllooollllllc::::;;::cc:::;;,,'',;cdO0KXXx:;,;:ldkOKNMMMMMMMMMMWNXXK0OOkxxxxxkO0XX0dc;,;::;,,,,:ok0KXX0Okxolc::;;;;,,,,;:::;;;;:::::cclllllllooollllllc:;;;,,;;;;;;,,,,,,,,,,,''''.''''.............                                                                                           ",
"...',,,;;:::ccllloooolllccc:::;;::::;;,,,,'',,:lk0KNWNkc;;:cdkOO0NMMMMMMMMWNNNNNX0OxocccccoxO0KOd:;;:cllc:;;;cdOKXK0Okxdolc::::;,,,,;;;;;;;::ccc::cc::cclllccccllllc:;;;;;:::;;;,,,,,,''''''''.....'.............                                                                                           ",
"..',,,,,;;;:::clloooooollccc::::::::;,,''''',:lx0KNWWXOl::ldkOOO0NMMMMMMMWXKKKKKK0xl:;;;;;cok00Odc;:lxkxxol:::okO0OOkxkkxoc::::;,,,,,;;;;,;:clc:::::;:::cc::::cllllcc::::::;;;,,,,,,,,'''''''''...'''''......                     ...                                                                       ",
"',,;;;;;;;;;;;::cclllloolllcc::::::;;,'..'',;:ok0XWWXKOoloxkOOO0XWMMMMMMWNK0OOOkkko:;,'',;:okO0Oxl:lxkOkkkxlc:ldkOOkkxkkxoc::c:;,,,,,,,;;;;:ccc:::;;;;;;;;;;:ccllccccc:::;;;,,,,,,,,,,,,'''''''....''.........             ........                                                                         ",
",;:ccc:::;;;;;:::::ccclllllccc::cc:;,''..'',;:dO0XNNXKOxxkOOOOO0NMMMMMMWNK00Odllll:,''''';lxOOOOkdldkOOOkOkdlccdkOkkkkkxolc::::;,,,,,,;:::::::;;;;,,,;;,,,,;cllc::::::;;;;;;;,,,,,,,,'''''''''''..'............      .   .......                                                                            ",
";coxkkxxddolcc:::::cccccccccccc::::;,'''''',,:lkO0KXX0OOOOOOOOOKWMMMMMMWN0O0kl;;::;''',,;cxO000Okdodkkkkkkkdc:cokkkkkkkdoolcc:;;;;,,,;;:cc::;;;;,,,,,,,,,,;:cc::;;;;;;;;;;;;;,,,,,,,,''''''''''''''...''''.....        .........                                                                            ",
"cdO0000000OOkxdoooollllccccccccccc:;,,,,;;,,,;:okO00OkkkxxkOOO0XWMMMMMWNK0kdo:;,,;,'',;:lxO0000kdllooddllooc;;coxkOOOkxddxdl:;;;;,,,;::cc::;;;;,,,;;;,,,,;;:::;;;;;,,;;::::;;;;;;;,,;,,,,'''''''''''''''''''....       ..........                                                                           ",
"oxO00KKXXXXXKKKK000OOOkxoc:::::cllc:;;;;::;;;;;:lodoloooccdOOO0NMMMMMWNKOkdol:;,,;;,;;:lxO000Okoc;;:;;;,,;:;;;coxOOOkkkkkxoc;;;;,,;::cccc:;;;;;,,,;;,,,,,;;;;;,,,,,,;::cccc:::;;;;;;;;;,,,;;,,,,'',,,,,,,''.....      .............                                                                         ",
"lodkO0KKXNWWWWWWWWNNNXKK0xl:::::clolc:;:::;;;;;:::ccccccccokO0KWMMMMMNK0kdolc:,,,;:::cokO00Okxlc:;,''''.',,,;:ldkOOkkkkkkdc;,,,;,;;:ccccc:;;;;,,,,'''',,,,,,,,,,,,,;::ccccc:::;;;;;;;;,,,,,,,''''',,,,,,''....      ...'''..........                                                                        ",
"oooodkO0KXNWMMMMMMMMMWWWNNKkoc:::clolc::c:::::::cccccc:ccldO00KNWWWMMNK0OOxl:;,,;coodxO0K0kdlc:;;,'.......';:ldkOOOOOOOkxl;,,,,,,;:ccccc:;,,,,,,''''',,,'''',,,,,,;;:::::;;;;;;,,,,,,,,'''''''''',,,,'''.....  .......',,'''........                                                                        ",
"loodxkOO00XNWMMMMMMMMMMMMMMW0occ::clllccclllooooolllc:::clok00KXXXNNNX000Oxl:,,,cdkOO0KK0kl;,,''..........';cokOO000OOkdc;,'''',;:cllcc:;,,,,;,,''''''''''''',,,,,,;;;,,,,,,,,,,,,,,,'''''''''''''''''''.............',,,,,''........                                                                       ",
"lodkOOO000KXNWMMMMMMMMMMMMWKxodxocccclccldkO00OOkxol::::cclxO0KKKK0KK00Oxolc:,,;cokO0KK0ko:,...............,cxOKKKK0Oxo:;,'''',,;:cllc:;,,,,,,,''''''''''''',,',,,,,,,,,,,,,,,,,,,,,,,''''''''.....'''''...........',;;;;,,,'........                                                                       ",
"ddkO0000KKKXNWMMMMMMMMMMMMW0dxKNXOdccccccd0KXXK0Okoc::::::coxO00OOOkkkkdc:cc::;::cdkO00Oo:,...............';oOKXXK0ko:;,''''',:cclool:;;;,;;,,,''''.'''''''''''',''',,,''',,,,,,,,,,,,,''''''''...............''',,;:::::;,,'........                                                                       ",
"OO000KXXNNNNWWMMMMMMMMMMMMMNKXWMMMN0xoc::lkKNWX00koc::;;;:cldkOxddoooolc;;::cccc::cloddo:,...............';lk0KK0Oxl;,'''',,;coddxxdl:;;;;;;;,,,''...'''''''''''',,,,'''''',,,,,,',,,,,,,,,,,,,,,,,,'''........'',;:::;;;,,''......  ..                                                                     ",
"00KXNNWWMMMMMMMMMMMMMMMMMMMMMMMMMMMMWXOoccoOXXX00xl::;;;;::coddllccccc::;;;:lolccc:;;:::,...............,;lk000kxl:;,'..',:codxkkkkxocc:::;;;,,'''''......''''''''''''''''',,''''''',,,,,,,,,,,,,,,,,,'',,,,,,,,'',,,,,,,,'''............                                                                   ",
"KKXWWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWXkllx0KK0koc:;;;;;;:cclccc::::;;;;;;:clllllc;,;:;,.............',cok00Oxoc;,'''',;coxkkkkkkkxdollc:;;,,,''''........''''''''''''''''''''',,,,,,,,,,,,,,,,;;;;,,,',,;;::c:::;;,'''''''..........                                                                      ",
"KNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNOld0KK0Odl:;;,,;;:ccc:::;;;,,,;;;;:cclllll:;;::,''..........,:lxOOOxo:;,'.'',;:ldxkkkkkkkxddolc::;;;;,,'''''...''''''''''''''''''''''''''''''',,,,,,,;;;:;;;;,;;;:::::::::::;,''............                                                                       ",
"XNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMKooOKK0Oxl:;;,,;:cc::;;;;,,,,,,;:::ccllllllcclc;;,'........,cdkOkdc:,'...'',;coxkkkxxddddoolcccccc:;;,,''''''''''..'''''''''''''''''''''',,,,,,;;;;;;;:::::ccccclllllcc::;;;;,,''..........                                                                        ",
"KXNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMKllk000kl:;;,,;;:cc:;;;,,,,,,,,,;::ccldddxkkkkdl:;,'......,:dOkdc;,'....'',;cldxxxdlccccc::::ccc:::;;,,'''''''''''''',,,''''''''''''''',,,,,;;;;;;;::ccloddxddddddddoolc:::;;,,'''.........                                                                        ",
"0KXNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNxcoO00Oxl::;,,;;:c:;;;,,,,,,,',,;:ccldkOO0OOOOOkdc:,,,,'',;coxd:,,,'...'',;:ccllc:::;;::;;;::::::;;;,,,,,,,,,,,,,,,,,,,,,,,,,,,'''''''',,,,,;;;;:::ccllodxxkkkkxxxxxxdolc::;;,,'''.......                                                                          ",
"0KKXNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWOc:d0K0Oxoc:;;;;::::;;,,,,,,,,,,;:cccldkOOOOOOOOOxl:;;;;,,,;:clc:,,'....',;;;;;;;;;;;;;;,,,;;;;,,,,,,,,;;;;;;,,,,,,,;;;;,,,,,,,,,,,,''''',,,,;;;;;::ccloodxxxkkxxdddddoollcc::;,,'''.......                                                                         ",
"0KXNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMW0l:oOK00kdl::;;;;::::;,'',,,,,,,;cccclooxkOOOkxddolc::;;;;;;;::cc:;,'....',,,'''',,,,,,,'''''''''''',,,,,,,,;;,,,,,;;;;;;;;,,,,,,,,,,,,,,,,,,,,,,,;;::cllooddxxxxxxxxdddollccc::;,'''..........                                                                      ",
"00KNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWXdcok000Oxl:::;;;;;::;,''',,;,,,;:ccccloooxkkxocc:::::;;;;;;::::cc:;'...............'''.........''''''',,,,,,,,,,,,;;;;;;;;;,,,,,,,,,,,,,,,,,,,,,,,,;;:::ccllodddoddxxxxdoolcc::;;,''''...........                                                                    ",
"00KKXNWMMMMMMMMMMMMMMMMMMMMMMMMWWWWWWX0xkOK000koc::::::;;;;;,''',;;,,;;:cccclodxkxl:;;,'',;;:::cccccccc:;,,''''.....................'''''''''''''',,,,,,,,;;;;;:;;;,,,,,,'''',,,,,,,,,,,,,;:::::cccloooloodddollccc::;;,,'''............                                                                    ",
"KKKKKXWMMMMMMMMMMMMMMMMMMMMMWNXXXXNNXK00KKK000kollccccc;,,,,,''',,,,,;;:cccclooooc;'......';:cdkxdllllcccc:::;;,''',,,,;;;;;,,,,,,,,,,,'''''''''',,,,,,,,;;;;:::::;;;,,''''',,,,,,,,''''',,;;:::cccllllcclllllccccc::;;,,'''..........                                                                      ",
"XNNNNWWMMMMMMMMMMMMMMMMMMMMMWNXKXXNNNXXXXK00OOxolllllc:;,',,,,',,,,,;;::ccc:cccc;,.........';cx000OOO00KKK0OkkxdoccldxkOOkxdoolccc::::::::::;;;,,;;,,,,,;;;;:::::::;;,,,,''''''''''''''''',,,;;::ccllccccc:::ccccccc::;;,,'''.........                                                                      ",
"KXXNWWMMMMMMMMMMMMMMMMMMMMMMMWWWWWMWWNNXK00OOkdolcccc:;,,,,,,''',,,,;::ccc:;;;;;'....    ...':x0KXNWWMMMMWNXKKKXXOkOXWMMMWWNXKxl;,,;lxOOkkkxxdolc:::;:::ccc:::cccc::;;;;,,'''''''''''''''''',,;;;:::c::::::::::::::::::;;,,'''.........                                                                     ",
"O00KKXNWMMMMMMMMMMMMMMMMMMMMMMMMMMMWNXKKK00Okdolcc:;;;,'',,,''''',,,;;;:c::;,''....       ...,:xKNMMMMMMWXxdddxk0XNWMMMMMMMMWKxc;'''c0WWWNXK0OOkxxdoooddddddooooolc:;;;,,,'''''............'',,,;;:cc:;;;;;;;;;;;,,;;;;;,,,''''..........                                                                   ",
"dk00KXNWMMMMMMMMMMMMMMMMMMMMMMMMMMMWXKXXK00kdlcc::;,,'''',,''''',,,,;;;;;;;,,'....        ....:OWMMMMMMMW0olllodx0NMMMMMMMMWKkol:;;ckNMMMMWWXK00OOOkkkkkkkkkkkkkxxoc::;;,,''''''............'',,,,;;::;;,,,,,;;,,,'',,,''''''.............                                                                  ",
"xO00XWMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNXXXK0Oxoc::;;,,,''''',,'''',,,,;;;;;;;;,'.......      ....;xXWMMMMMMWKoccloodx0NMMMMMWNKxdollox0NMMMMMMMWNX00OOkkOOOOOOOOOkkkkxdlcc:;;,,'''''...........'',,,,,,,;;,,,,,,,,,,,,''''''''''.............                                                                  ",
"O0KKNWMMMMMMMMMMMMMMMMMMMMMMMMMMMWNXKK0Okdlc:;;,,''''''',,,,''',,,,;;;::::;,''........   .....';dNMMMMMMMNkcclloodkXMMMWNK0Okkkk0XWMMMMWWWNNXK0OOkkkkkkkkOOOOOOOkkkkkxdolc:;,''''''''......'''',,,,,,,,,,,,,,,,,,,,'''''''''''........  ...                                                                 ",
"0KXXNWMMMMMMMMMMMMMMWMMMMMMMMMMWNXK0Oxdllc:;,'''''''.'',,,,,''''',,;;:ccccc:;,,,,;;,...........',cox0NWMMMN0xoooodkXWMWX0OKXNNWWMMMMWNXK0OkkxxxxddoddddxkkkOOOOOOOOOkkkkxol:;,''''''''''''''''',,,,,,,,,,,,,,,,,,,,''''....'''.........                                                                     ",
"00KXXNNWWWWWNWWWWWWNNWMMMMMMMWNK00Oxoc::;;,'..........''',,,'',,,',,;:loooolc::clooc,...............':xXMMMWNX0OkkOXWMWNNWWMMMMWWNXK0kxdoollloollllllllodkkkkkOOOOOOOkkkkkdl:;,''...'''''''''''',,,,,,,,,,,,,,,'''''''.................                                                                     ",
"000KKKKXXXXXXXXNXXXXNWWMMMMWNX0Okxoc:;;;,,'.............''''''',,,,;:clooddddodxkkkdc'.........'''''',;oKWMMMMMWWNNWMMMMMMMMWNXK0OOkxxdddddooddolllllllloxkkkkkOOOOOOOOkkkkxoc;,''....''''''''',,,,,'',,,,,,,,,,'''...................                                                                      ",
"OOOO00000000KKKKKKKKXNNWWWNXK0kolccc::;,,'................'''',,,;;:clodxkkkkkkOkkkxo:,''...',,;;;;clodxOKNWWMMMMWWWWWMWWWNXK0OOOOOOkkkkkkkxxxxolllcccccllodxkkkkOOOOOOkkkkkdl:;,''....'',,,,,,,,,,,'''''''',,;;;,,'''.................                                                                     ",
"OOOOOOOOO0000000000KKXXNNNK0Odlccccc:;,,''..................'',,;;:clodkkkOOOOOkkkkkxxdoc:;;;:cc::cldkkOO00KXXXXXXXNNWWWWWNXK0000OOOOOOOkkkkkxolcc:::cccccclodxxkkkkOOOOOkkkkdl:,''.....''',,;,,,,'''''''''''',,,;,,,''..................                                                                   ",
"OOOOkOOOOO00000000000KKXXK0Oxlcccccc;,''....................'',,;;:cloxkOOOOOOOkkOOkkkkkxxdoolloolllldkkkOOO000KXNWWMMMMMMMWNXK0000O0OOOkkkkkxdoolc::ccccc:ccclloxxkkkkkOkkkkkxoc;,''...'''',,,,,,''''',,,,'''''',,,,,'''..................                                                                 ",
"OOOxdxkOOOOOOOOOO0000KXXX0Oxolllllc:;,'.....................'',,,;;:cloxOOOOOOOkkkkkkkkkkkkkxdoodoooodkOOOO0KXNWMMMMMMMMMMMMWNXKKKK000OOkkkkkkkkxdolccc:::::::cccclodkkkkkkkkkkxdc;,'''''.''''''',,,,,,,,,,''''..''',,''''.................                                                                 ",
"ddxdoodkOOkkkOOOO0000KXXK0xoollllc::;,'.....................''',,,;:clldkO0OOOkkkkkkkkkkkkkkkkkkkkkkkOOO000KNWWMMMMMMMMMMMMMMWNXKKK00OOOkkkkkkkkkkxxxddolc:;;;;:::::codxkkkkkkkkxl:;,''''''''''''''',,,,,,,,,''''....'''''.................                                                                 ",
"OkdooooodooloxOO0000KKXKOxollooooc:;,''...................''','',,;;:cldkOOOOkkkkkkkkkxxxkkkkOOOOOOOOO00000KXNWMMMMMMMMMMMMMMMWNXXK0OOOOOOkkkkkkkkkkkkkkxl:;;;;;,,;;:::cldxkkkkkdl:;,,,,'''''''''''''''''',,,,''''''.......................                                                                 ",
"WWXKkxdolcccldk0000KXXKOdlclloddol:;,'..................'',,,;;;;,;;:cdkOOOOkkkkkkkkkxdodkkkOOO000000000KKKKKXNMMMMMMMMMMMMMWWNNXXK00OOOOkkkOOOkkkkkkkkxdlc:;;;,,,,,,,;:clodkkkkxo:;,,''''....''''''''''''',,,,,''''''....................                                                                  ",
"XXNXK0OxlcccldO00KKXXKOdlcccloddoc:;'..................''',,;clll:;;:ldkOOOOkkkkkkkkkkddxkOOOOO000000000KKKXXNWMMMMMMMMMMWWNXXXKKK000OOOkkkkOOOkkkkkkxdol:;;,,,,,''''',;:cldxkkkkxoc;,''''.......'.''''''''',,;;,,,''''''...................                                                                ",
"0000000koccloxO000KK0kocccccclollc;,''................',,,;:coxkxo:;:ldkkkkkkkkkkkkxxkxxxkkkkOOOOOOOOO000KKXNWMMMMMMMMWWNNXKKKKKK000OOOOOkkkkkkkkkkxolcc:;,,''''''''''',;;cloxkkkkxoc;,'''.............'''',,,,,,,,,,,,''''..................                                                               ",
"dooooxkkoccllxO000Okolc::::::cc::;,,''..............',;;:::codkOOxlccldkkkkkkkkkkkkxddxddxkkkOOOOOOOOOOO0KKXNNNNWWMMMMWNXKK0000OOOOOOOOkkkkkkkkkxddlc::;;;,'''''....'''',;:cloxkkkkxo:;''...'............'',,,;,,,,,,,''''....................                                                              ",
"c::::cooolllldk00koc::;;;;:::::;;,,'.........   ...',;::ccclodxkkdolllldxxkkkkkkkkkkxdolloxkkkOOOOOOOOOOO00KKKKKKXNWMMMWNK00OOOOkkkkkkkkxxxxddoolcc::;;;,,''''''.........',;:coxkkkxdc:,'.................''',,,,,,;;;,,''...................                                                               ",
"xl:::ccllllcclxOkl:;;;,,,,;;::;;;,'........    ...',:::clloooodxdollcccccloddddxxkkkxdollodkkkkkkOOOOOOOOO00KKK000KKXNWWNXK0OOOkkkxdoddooooollcc::;;,,,'''''''''..........',;:ldxkkkxoc;,'..................''''''',,,,,'''..................                                                               ",
"koc::::cclccclll:;;;;,,,,,,;;;;;,,'...............,;:ccclodddddollc::;;::cccllloodxkkkxxdddxkkkkkkOOOOOOOO000000OOOO00KXXXK00OOOOkxdolccccccc:::;;;,,''''.....'............'',:coxkkkxoc:,'.................'',,'''..'''''''.................                                                               ",
"::::::::ccc:ccc:;;:::;;,,,,,,,,,''...............',;:ccccldkkxdlc:::;;,,;:cc::clllccllodddoddxxkkkkOOOOOOOOOOOOOOOOkkkOOOOOOOOOOOOkxoollcccc:;;;,,,,,,'''.................',,,;:coxkkkxdoc:;,,'..........''''',;;;,''.........................                                                              ",
":;;:::c::::::cccloolc::;;;;,,,,,''......     ....',;::c:ccloolcc::::;;;;;:::::ccc:;;,;;:clllllodxkkkkkkkkOOOOOOOOOOOkxddxkkOOOOOOOOkxdxxdolcc:;;,,,,,,'''..'''''...........',,;:cldkkkkkxxdolc:;;,,''...'''''',;;::;,,'''.....................                                                              ",
"c::::ccccc:::clokOOkxdlcc::;;;,,,'......     ...',,;;:cccllcc::cc:::;;:;;;;;;;::::;,,,,;::cccllloddddxkkkOOOOOOOOOOOkxollodxxkkOOOOkkkkkkxdolcc:;,,'''''....''''''..........',,;:codxxkkkkkkkxxddolc:;,,,,;;;;;;;;::;;,,''.....................                                                             ",
"c:;;::clllcc:ccokOOOOOkxdoc:;;;,,,''....     ...',;;;:cllllc:::::;;;;;;;;,,,,,,,;;;;;,,,;:::cccllooodxxxxxkOOOOOOOOOkxolccccloddxxxxxxkkkxdoccc::;,''......................'',;;;::cclloodddddddddolc::;;;;;;;;;;;;;;;,,'''....................                                                             ",
":;;;;:cloolc::cokOOOOOOOOkxdollcc:::;,...    ....,,,;clooollc::;;,,,,,,,,,'''''',,,,,,,,;;:::cccloooooollodxkOOOOOOOOOkdllccc:::cccccclool::;;;;,,''.......................'',;:;;;;;;;;;;::::;;;:::;;,,,,,,,,,;;;;;;,,,'''.....................                                                            ",
"::::;;::cccc::cldOOOOOOOOOOOkkkxdolll:,'...   ...',;:lxkkxolcc::;;,,,''',,'''''''',,,,,,,,,,:cclllllccccllldxkOO00KK00OOkxdolc:;;;;,,,,;;;;,,,''''..........................''',,,,,,,,,,,,,,'''''''''''''''''',,,;;;,,,'''.....................                                                            ",
"llcc:;;:::ccccclodkOO00000OOOOkkkkxxdoc:,........',cokOOOxoc:::::::;,,',,,''''.....'''''''',,;:clccc:::::clodxkkO0KKKK00OOOkkxdlc;,,,,,,,,,,,,,''..............................''''''''''''''.............''''''','''''''''......................                                                           ",
"cccc:;;;;:::cclllloxO00KKK0OOOOOOOOOkkxdl:;,'''';cok0KK0kdl:;,,,,;;;;,,,,,'''...........'''',;;::c:::::::::clooodxkO00000OOOOOOkxdoc:::;,'',,;;;;,'.................................''''....................''',,,,,'''''''''....................                                                           ",
"dxkxl::;;;:::cccccclxO0KKXK0OOOOOOOO00OOkkxxxdddxkOOOOkxolc:;,'''''',,,,,,,''''.......''',,''',,,,;;;;;;;;,;:cc::clodxxxxkkxxxxxkkkkxool:;;;;;::::;;,''''''...''''''........'........'''....................''',,,,,,'''''''''...................                                                           ",
"OOkdlc::;;::::ccccccldOKXNNX0OkkOOO0OkdddxkOOOkkkxdoolcc::::;,,,''''',,,,,,,,,,,,,,,,,,,;;;;,,,,,,,,,,;;,,'',,,,,,;;;:::ccccccclloddxkkxdooc:;:::::::::;;;;;,,,;;:::,''...''''''''...''''''.............'',,,,,,;;,,'''''''......................                                                           ",
"ollccllc:::::ccllcc::coOKNWWX0OOOOOkdlccclodddoool:;;::::;:::;;;;;;;;;;:::cloolc::::ccllc::::;;;,,,,,,,,,''''''''''''',,,,,;;;::ccllodxkOOkkdolllcclllllccccccc:cclooc:,,'''''''''..''''''''''.........'',,,,,,;:::;,,''''.........................                                                         ",
"llloxkkxoc::::cllllc:::lx0NWWNK00kdlc:::::ccccccc:;,,,;;;;;:c::ccclllcclldxkkkxocccldkOOkxdooolc:;;,,,,'''.............''',,,;;::cccldxO0000OOkkOkkkxxdddooooooolllodxdl:;;;;,,,,''''''',,,,,''''''''',,;;;;,,'',;;::;;,'''........................                                                         ",
"looxOO000koc:;:cllllc:;;:lkXNWN0xl::::;;;;;::::::;;,,,,,,,;;::::::ccllcccllllc::;;;:lodxxxkkOOkkdl::::;,'................'',,;;::cloxO0KKKKKKKKKKXXXXXKKK00Okkxxddooodddolc::::::;,,'''',;;;;;;;;;;::cccc::;;;,'''',;::;;,''.......................                                                         ",
"lodkO0KKXKOoc:::ccllcc:;;:lk0Oxc,'',;::;;;;;;;;;;;;;;;,,,,;::::cccccccccllc:;;,,',,,,,,;;:cloooooc:::;;'.................'',;;::ccoxO0KXNWNNNNWWWWWWWWWWWWNXK00OOOkxxxxddolcccccc::;,,,,,,;;::ccllllodxxdolc:;;,,''''',;;,,''......................                                                         ",
"lokO0KKKKK0Oxlc:::::cc::::clll:'...',;:;::;;;;;;;;;;::;;;:cooddxxkkxdolllllol:;;;;;,,,,'''',,,''''',,,,,'.......    ....'',;::clodkO000KXNWWNNNNWWNNXXXXXXXKKK0000OOOOOkxdollc::::::::;;;;;;;::cooddddxxkkxoc:;,,,''...'''...........................                                                       ",
"ok000KK000000koc:;,;;;;;;;;:::;'...',;;;;:;;;;;;;;;::::;:coxkkkOO0OOOOkkxxkkxolccccc:::;,'''.............''''.....   ...',;:coxOO00000OOkO0KKKKKKKK000000000OOOOkkOO0OOOOkxolccc:::::::::;;,,;:ccloooodddddoc::;,,''..................................                                                      ",
"k000000OOO0000koc;,,''',,,;;;;;,,',,;;::ccc::;;;;;;:::::;;:ccllooddxxkkkOOkkkkkkkkkkxdlcccc:;,'.........................',;:ldO0KKKKK0OkdodxkOOOOOOOOOOkxxxxkxxdooodxxxxkOOkxollccccccccc::;;;;:ccloodddddolc:;;,,''..................................                                                      ",
"00000OOOOOOO000xl:;,''',,;;::::;,'',,;;:cclllcc::::;:::::;;;;;;;;::::ccloolcclodxkkxxxdxxxxxxoc;,,,''...................',;:cok00KKXK00OxollodxkkkkkkkkkdollllllccccllclodkOOOkdllloooolllollc:cclllooddoolcc:;;,,,''..................................                                                     ",
"000OkxdxOO00000Oo:;,'',,;;::::::;''''',;;:cloolccccccccc::;;;,,,,,;;;;;;::;;,;::cccc::::lolllccc:;,'.................',,,,,;;:ox0KKK000Okxdllcloddddxxxxdlc::::::;;:cc:::clxOOOOkdllloollllodxddddxxdddxxdoc:::;;,,''....................................                                                   ",
"00OxdooxOO000000xc;,',,,;;:::::;;,''',,,;;:::cccc:cclllcc:::::ccc::;:::::;;,,;:::;;;;;,,,;;;;;;;::;,'................',;clooolccok000OOOOOkdoccclolllooolcc::;,,,;;;::::;;:ldkOOOkxolllollcclodxxkkkkkxkkkxdoc:;;,,'........................................                                                ",
"OkdooodkOO000KKKkl:;,,,,,;;;;;;;,,,,;;;;;::::::::;::ccc:::::::clllcc::ccc::;;;:cc::::;;;;;;;;;;;;;;,,''..........',,,,,;:ldO00Okdddddddxkkkxdoccccccllllc::::;,,,,,,,;;:;;;:codxkkkkdlcllcc:::ccldkkxxxxxkkkxdl:;,''............................................                                            ",
"xoollodkOOO0KXXKOxlc;,,,,,,,,,,,,,;;;::::::::::::;;;;;;;;;;::::::;;:::::c::;;;::::::::;;;:::;,,,,,''.............',;;::ccccldkO0KKOkdlcclllloolc:::cccccc::;;;;,,,,,,,;;:::;;:clodxkxolccc:::;;;;cldoollllodxdoc:;,'.....................................''''''....                                         ",
"lllllloddkO0KKK0KK0Oo:;,'''',,',,',,,;;;;:::cllccc::;;;;;;;;::::;;;;::::::;;;;;,,,,,,,,'',,;,'...............''...';:clxkkxolcloxOO0OOxolcc:cccc:;;;::cccc:;;;;;;,,;;;;;:::;;;;::cloxxxoc::::;;,,;:cllc:;;;:ccc:;,''.....................................''',,,,''.....                                     ",
"lccllloodk000KKXNWWN0o:;,'''''''...'',,;;;;::ccccccccc:::;:::::::;::::::;;;;,,,''..'''.......................',,'..',cd0KK00Oxocccldkkxdoollc:::;;,,,;;::c::;;;;;;,,;;:;::::;;;;;;;:ldkxdc::::;,,,,;;::;;,,',,;;,'''......................................'',,;;;;,,,''....                                 ",
"llllooodxO000KXWMMMWX0d:;'.............''',,;;;;::::::::;;;::;;;;;;;;;;,,,,,,''..........  .............',''',;;:;,'',:dO0000Oxolc:cclllllllllc:::;,,,,,;:::;,,;;;,,,;::::cc:;,;;;;;:cdxxoc:::;,,,,,,,,,,,''''''''.......................................'''',;:ccc::;;;,,,'...                             ",
"cllllooodxO00XNWMMMWXKkl:,'................'''',,;;;;;;,,,,,,,''...................  .....   ...........':ddolclxOdc,'';:lodxxolllccc::::::::cllllc:;,,,,,;;,,,,,,,,',;:::clc:;,,,,,,;cldol:;;;,,,'',,,,,,'''.............................................'',,;:looolc::::;;;,'..                           ",
"ccllllllox0KNWMMMMWNXK0xl:;,''.................'',,'''.............................  ..............''....,dXWNKOxk00xl;,,::::ccccc:::::;::;,,;:cloolc:;;,,,,,,,,,,;;,',;:ccccc:;,,,,',;:cccc;,,,,''''','''''..............................................'',,;:codddolllcc::;;,,'...                       ",
"ccllllllx0XNWMMMMWNXKK0xolc:;,''.................'''............. .     ...........................',;;,',;o0NMMN0xdk0Oo:,;;;;;;;::;;;;;:c:;,',:clooolc:;,,,,,,,,,,,,,,,:::::::;,,,''',,,;:c:;,,,''''''''''...............................................'',,;:cloddddxxddolcc:::;;,'..                    ",
"ccccllox0KNWMMWWNXKK0Oxooooc:;,,,''...............''........          .............................';cddoccccoOXWMXklldkxl;,,;;;;;,,,,,,;::;,'',;:clllllc;,,',,;;,,,,''',;:::;;;,,'''''''';::;,,,'''...'''''..............................................'',;;:llodxxxxkkxxxxdoolc:;;,'..                  ",
":::cldk0KXNWWNXK0000Okooool:;;;;;;;;,'.......  ............        ........''''''''',,,,,,''''''',:lxkOkkddoolcoONWN0dlclcc:;,,,,,,,'.'',;;;,'',,;;:ccccc:;,'''',,,,;;,'',;;;;,,,,''''''..',,,,''''''..'''''...........................................''''',;;clodxxxxxkkkkkkxxddollc:;,'..                ",
"::coxO00KXXXK000O00Okdllol:;,,;:codoc,....................     .......';ldxxocll:::ldkkkko:,,;::;::c:;,'.',;;:::;cdxOOkdc;;;,,,'..''....',,;;,''';;:cccc:::;,,''''',,;:;;,;;,,'''''.........''''''''''''''''............................................'''',;::coxxxxxxkkkkkkxxxxoollcc:;,'..              ",
":cokOO000K00OOOOO0Oxolllc:,,,,;:oO0kc;'............................';cd0NWWWKkxxxxkkkkkOkd;...'....           ... ..';clc:;,'',,'......'',,,,,'''',:looolc:;;,,'''''',;;;;;::,''...................'''''..''............................................'''',,::loxxxxxxkkkkkkkkkxxddocc::;;,,...           ",
"loxOOOOOOOkkxxkOOOdlcccc:,'',;:lkK0o;;,;,,'.........',,'.......',;:oOXNMMMMMWXkol:;'.......                            .,;;,'.''''......',,,,''..'';:loddolc:;,''''''',,,,;;:;,''....................''''.............................................'''''',,;:ldxxkkxkkkkkkkkkkkkkxxdlllccc:;,'..         ",
"ldkOOOkxdooloxOOkoc:ccc:,''',;cd00x:;;;::;,'......',:col;,'',,;:lokKWMMMMWN0xc,..                                       .';;,''''........'',,,''...',;:cloool:;,''....',,,,,;;,,''.....................'''..............................................'''',,;cldxkkkkkkkkkkkkkkkkkkxxdolllcc::;,..        ",
"odxxdollcccldkkdlc::cc:,'',,;:lkOxc;;;:::;,'''''',;:okOxc;,,;;cdO0XWWWNKko;..                                            ..,,,,,,'........''''',''''''',;:lllc::;,'....',,,,,,,'''''....... .............''.............................................',,,,;:cldxkkkkkkkkkkkkkkkkkkkkxxdollccc:;,'..      ",
"ooolc::::ccoddlc:::::;,'',;;:cdkxc;;;;::;,''''''',;lkOxlc:;;:lk00KXXXOd:..                                                 ..',,,'.........''''','''''''',;:cc:::;,'....',,,,,'''..........  ...........................................................'',;;;:codxxxkkkkkkkkkkkkkkkkkkkkxxxdoollcc::;'..   ",
"lc::;;;:cclllcc:;;:;;,'',;;;:codc;;;;;;;,,'''',,,;cdkxlc::::cx00OOOkxl,.                                                     .',,,''........'''''''',,'''',,;::::;;,'.....''''''.........................................................................',;;::cloxxxxkkkkkkkkkkkkkkkkkkkkxxxddoollllc:;,...",
":;;;;;;:ccccc:;,,;;;,'',;;::clol:;;;;;;,,,,,,,,,;:oxxlc:::cloddollllc,.                                                       .',,,'''......''''''''',,,,',,,,;;;;:;,'.......''..........................................................................'',;:cclldxkxkkkkkkkkkkOOOkkkkkkkkxxxxxxddolc:;,'..",
",,,,;;::c:::;;,,,,,,''',;::cclol:;;;;;,,,,,,,,;;:lddlccccloolcc::::;,.                                                        ..''',,,'.....''''''''',,,,'',,;,,,,;;,''..................................................................................'',;;:clodxxxkkkkkkkkkkkOOOOOkkkkkkkxxxxxxdolc:;,'.",
",,,,;;;:;;;,,',,,,,''',,;:cclolc:::;;,,,;;;;;;:clolccccllcc::::;,...                                                          .,,'',;;'....''''''''.''',,'',,;;;,,',,''..................................................................................'',;;;::lodxkkkkkkkkkOOOOOOOOOOkkkkkkxxxxxxxddlc:;,",
",,,;;;;;;,,''',,,,,',,,;;::cllc::::;;,,;:cc::cllllc::cc:;;,,,'..                                                              .',''',,,'...'',,,''...''''''',,;;;,,,'''...................................................................................'',;::::cldxkkkkkkkkOOOOOOOOOOkkkkkkkkxxxxxxxxdoc:",
",,,,;,,,,,'''',,,'',,,;;:::ccc:::;;;;,;codollollc:::;;,'....                                                                   .''''',,,''..'',,,'.......'''',,,;;,,,''....................................................'..............................'',,:cccccloxkkkkkkkkkkOOOOkkkkkkkkkkxxxxxxxxxxdoo",
",,,,,,,''''',,,,'',,,;;;::::::::::;;;;cdOOxdolc:;,,,,,'.                                                                       .,,'',,;;,'''''',,,''.......''',,,,,,,,'.................    ................................''..........................'''',,;:cccclloxxkkkkkkkkkkkkkkkkkkkkkxxxxxdooolllll",
",,,'''''''',,,,'',,,,;;;;;::::::c:;;:cxO0Oxoc:,,''''''..                                                                       .,;,'',;::;,''''',,,,,'.......',,,,,,,''.................     ................................''........................'''',,,,;:ccllllodxkkkkkkkkkkkkkkkkkkxxxxxxxdolllclll",
"'''''''''',,,,,,,,,,,;;;;;:::::ccc::cx00Odc;'.....                                                                             .,;;,,',:::;,''''''''''''......'''''''''...................    ........................................................'',,,;;;;;:cclllllodxkkkkkkkkkkkkkkkkkxxxxxxddolllccll",
"''.''''''',,,,,,,,,,;;;;;;::::ccc::cdOOdc,..                                                                                   .,;;;;,,,;::;,''''''''''''......'''''''.....................     ......................................................',;;;:::::::cloooooooxxkkkkkkkkkkkkxxxxxddoooollcc::::",
".'''''',,,,,;;;,,,,,,,,;;;:::cccc:cloo:'.                                                                                      .',;;;;;,,;;;;;,''..'''''''........'''.....................       .................................................''..';:c:::::cccclodddooodxxkkkkkkkkkkxxxxxddoollllllc:::;",
".'''',,,;;;;;;,,,,,,,,,;;;;::ccccllc;..                                                                                        .',,;::::;;,,;;;,''...'''''...............................       ...................................................'''',;cccc::clllllloddxddxxxxkkkkkkkkkkxxxdoolllllooollcc",
"'''',,;;;;;,,,,,,,,,,,;;;;;::cccllc,.                                                                                          .'',,;::::;,,,,;;,,'.....''...............................      ...................'''..............................'''',,;:cccclooolcclodxxxxxxxxkkkkkkkkkkkxxdoolllllollllc",
"'',,;::;;,,,,,,,,,,,,;;;;;:ccccccc:,..                                                                                         .',,,,;::::;,'',,,,,'......................................     ....................'''.............................''',,;;::cclooddlccccloddxxxxxxkkkkkkkkkkkkxxdooolllcc:::",
",,;:::;;,,;;,,,,,,,;;;;;::ccccccc:::;,.                                                                                         .,,;;;;;::;,,',,,,,'''....................................     .......................'...........................'''',;:::;::clodddolcccclloddxxkkkkkkkkkkkkkxxxdoollcccc::",
";::::;,,;;;;,,'',,;;:::::ccccccc::cc;'.                                                                                         ..,;;;;,;;;;,,,,,,''''''...............  ...................  ....................''.............................'',,,,,;::::;:cldxxxdoollllloodxkkkkkkkkkkkkkxxxdoolccccccc",
"::::;;,;;;;,''',;;::::::cccc::ccoxkd,.                                                                                    ..     ..,;;;,,,;;;;,,,''''''''................ ........................................''..............................',,;;;;;::::;::ldxxxxxdddddoddxxkkkkkkkkkkkkkxxdoolccccccc",
":::;;;;;:;,'''',;::::::cccc::cloONXd'                                     ..                         ..........         ..,;'.    .,;;;,,,,;;;;,,''','''''........................................................................................',;;;;;;;::::;:coxxxxxxxxxxxdddxxkkkkkkkkkkkkxxdolcc:ccllo",
" ",
" ",
" ",
" ",
" ",
".'''''.",
"'x00KKX0xdxxl'...",
".oOOOO0KKKKKKXXK00Oo:;;.",
".d00O000K0KKXXKXXNX0xl;;.",
"'lkkkO00000KXXKKXXNXNXXOdc'",
".lkkxxkkkO0000000KXXKXXKKKKKX0o::.",
"lOkxddxkOO000KKKKKKXXNNNXXKKXKKKKKKKXk;                                                                                                                                               ...............",
".d0kkxkO0000KKK00KKKKKKKKKKKKKKXXKKKXKXXk                                                                                                                                   .',,,:loooodk0000O00000000kdoool:,. .,,,'.",
".xK000KKKKKKKKKKKXXKXNXKKKKKKKKKKKKKKKKKKKkc'.                                                                                                                     .,:llllloxOKXKKKKKKKKKKXXKKKKKKKKKKKKKXXKKKOkOKKK0kxkkoll;'.",
".xX0KKKKKXKKKKKXKXKKKKKKKKKKKNNKKKKKKKKKKXXKX0c''.                                                                                                        .':ccclxOKNNNKKKKKKKKKKKKKKK0KKKKKKKKXKKKKKKKKKKXKKKKKXKKKKKK0KXNXKKKOdl,....",
":0KKKKKKKXXKKKKKKKKKKKKKKKKKKKKKKKKKKKKKXKKKKXXKKKo.                                                                                                   .;oxOXNNNNNNXXXXXXXKKKKXXXKKKKKKKKKKKKKKKKXXXXKXXXKKXXXXXXXXXKKKKKKKKKKKKKXXKOO0ko:'.",
"'OXKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKkXXKKKKKKKKKKKX0c.                                                                                           .',,,ck0XXXXXXXXXXXXXXNXXXXXXXXNNXXXXXNNXXXXXXXKKKXXKKKXXXXXXXXXXXXKKXKKKKKK00KKKKKKKK00KK0kdl:.",
",0XKKKKKKXKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK000000KNKl.                                                                                    .,cdkkOKNXXXXKXXXXXXXXXXXXXNNNNXXXXXXNNNNXXXXXNNNNNNXXXXXXXXXKXXXXXXXXXXXXKKKKKKK00000KKKXXXXXKKKKKKXKkl;.",
".dXK0KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK000000KXXKkl.                                                                             .:ok0XNNXXXXXXXXXXXXXXNNNNNNNNNNNNNXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXKKKKKKKKKKKKKXXXXNNNXXXXXXKKXXXKkd:'.",
",kK000KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKXXKK000000K0KKXOo;.                                                                     .';ldOXNNNNNNNXXXXXXXXXXXXNNNNNNNNNNNXXXXXXXXXXXXXXKKXXXXXXXXXXXXXXXXXXXXXXXXKKKKKKKKKKKXXXXXXXXNNNNNNNNNNNXXXXXXKKKXXKOd,.",
":K000KKXXKKKKKKKKKKKKKKKKKKKKNNNXXNNXXKKKKKKKKK000O00OO0KKXOc'                                                               .;oxk0KXXKKKKKNNNNNNNNXXXXNNNNNNNNNNNNNNXXXXXXXKKKKKKXXXXXXXXXXXXXXXXXXXXXXXXXXXKKKKKKKKKKXXXXXKXXXXNNNNNNNNNNXXXXXXXKKKKKKKKXKOl.",
":00KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKXKK000KKKK00OO0O00O0KKXXkl'                                                         .cok0K0O00KKKKXXNNNNNNNNNXXNNNNNNNNNNNXXXXXXNNXXXKKKKXXXXXXXXXXXXXXXXXXXXXXXXXXXXXKKKKKKKXXXXXNXXXXXXXXNNNNNNNNNNXXXXXXXXXXXKKKKKKKOl'.",
"lK0KKKKKKXXKKKKKKKKKKKKKKKKKKNNNNNNNNNNXXKKKXNXK0000OOOOO000KXNXkdc.                                                  ,ldOK0O0000KKXKKKXNNNNNNNNNNXXNNNNNNNNNXXKKKKKKKKNNNXXKKKXXKKKKKKKKXKKKKKKKKKKXXKKKKKKKKKKKKKKKKKXNNNNNNNNXXKKKKKKKKKKKKKKKKKKKKKKKKKKK0x:.",
".xXKKKKKKKKKKKKkkkkkXXNNNNNNNXNNNNKKKKKKKKKKKXXK000OOOOOOOOO0KXNNNOc;'.                                          .,lxKXK00O00KKKKKNNNNNKKKKKKKXXNNNNNNXKKKKKKKKKKKKKKKKKKKKKKKXXKKKKKKKKKKKKKKKKKKKKKKKKXXNNNNNNNNNNNNNNXKKKKKKKKKKXKKXKKKKKKKKKKKKKK0000Kl",
",OXKKKKKKKKKKKKKKKKKKKKKKKKKKKXXNNNNNNNKKKKKKKKXXKKK0OOO00OOOO0KXXNNNKOd:.                                    .,oOKXKKKXKKKKXXNNNNNNNNXXXXXXXXXXXXNNNNXXXXXXXXXXXXXXXXKKKKKXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXNNNNNNNNNNNNXXNNXXXXXXXXXXXXXXKKKKXXXXXXXXXXXKKK00Okd;",
"cKK0KKKKKXKKKKKKKKKKKKKKKKKKKKKKXNNNNNNNNNNNXKKKKKXK0OOOOOOOOO00XXKKNNNNKOol;'.                          .';dOKKKKKXNNNNNNNNNNNNNNNNNNNNNNXXXXNNNNNNNXXXXXXXXXNNXXXXKKKKKXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNXXXXXXXXXXXXXKKKXXXXXXXXXXKKK0OOO0O;",
".cO00KKKKXKKKKKKKKKKKKKKKKKKKKXNNNNNNNNNNNNNNNNNNXKKKKKKK0OOOO0OOO0KXKKKXNNNNNNNNd.                      .cx0KKXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXNNXXXXXXXXXXXXXXXXNXXXKKKKKKKKXXXXXXXXXXXXNNNNNNNXXXXXXXNNXXXNNXXXXNNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXXXKKKKKXXXKK000KKK:",
".oO00KKKXXXXXXXXXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNXXXXXXKK0OOOOOO00KKXXXXXXKXNX0xc,..      .''      .;kK000KXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXXXNXNNXXXXXXXXXXXXXXXXKKKKK0KKKXXXNNXXXXXXXXXXXNNNXXXXXXXXXXXXNNXXXXNNNXXXXXNNNNNNNNNXNNNXXXXXXKKXXXXXKKKKXXXXKKKKKKXk.",
".d0O00KKKXXXXXXXXXXXXXXXXXNNNNNXXXXNNNNNNNNXNXXXXXXNXXXXK0OOOOOOO00KXXXXXXXXXXNNXKOxodkkxOKKkooc:oOXXKKKXXNNNNNNNNNNXXXXXXXXXXXNNXXXXXXXXXXXNNNNNNNNXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXNNXXXXXXXXXNNNXXXXXXXXXXXXNNNNNNNNNNNNNNNNXXXXXKXXKKKKKKXXXKKKKKXXXXl",
".x0O0KKKKKXXXXXXXKKXKXXXXXNNNNNNXXXNNNXXNXXXXXXXXXXXXXXXXK0OOOOOOO00KXXXNXXXXXXNNNNNNNNNNXXXXXXXNNNNNNNNNNNNNXXXXXXXKKKKKXXXXXXXXKKKXXXXXXXXXXXXXXXXXXNNXXXNNNNXXXXXXXXXKKKXXXXXXXXXXXXXXXNNNNXNNNNNNNXXXXNNNNNNNXXNNNNNNNNNNNNNNNNNNNXXXXXXKKKKKKKKKKKKKK00KKKKO,",
",xO00KKKKKKKXXXKKKKKKKKKXXXXNNNXXXXXXXXXXXXXXXXXXXXXXXXXNXKOOkkOOOO0KXXNNNXXKKXXXNNNNNNNNNNNXXXXNNNNNNNNNNNNNNNNNXXXXXXXXXKKKKKKXXKKXXXXXXXXXNNNNNNNNNNNNNNNXXXXNXXNNXXKKKXXXXXXXXXXXXXXNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNXXXNNNNNNNNXXXXXKKKXKKKKKKKKKKK00Kl",
".l0KKKKKKKKKKKKKKKKKKKKXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXNXK0OOOOOOOO0XXXXXXXXXXXXNNNNNNNXXXNNNXNNNXXXXXNNNNNNWWNNNNNNNNXXXXXXXXXNNXXXXXXXXXNNNNNNNNNNNNNXNNXXXNNXXXXKKKKKXXXXNNXXXNNNNNNNNNXXXXXNNNXXNNNNNNNNNNNNNNNNNNNNXXNNNXXXNXXXXNXXXNXXXXXXKKKKKKKKXXXK00x.",
",d0000KKKKKKKKKKKKKKKKKKXXXXXXXXXXXXXXXXKKKXXXXXXXXXXXXXXK0OOOkkOO000KKKKKKXXKKXXXXXXNNXKKKKXXXXXXK0KXNXXXNNNNNNNNNNNNNNNNNNNNNWWWNNXXXNNNNNNNNNNXXXXXXXXXXXXXNNXXKXNNNNNNNXXXXXNNNNNXXXXXXXXXXNXXXXNXNNXXXXXXNNNNNNNXXXNNNNNXXNNXXXNNNNNNNXXXXXXXKKKKKKKK000Kc",
";d000KKKKKKKKKKKKKKKXKKKKKXXXXXXXXXXXXXXXXXXXXXXXXXXXXKKKKK0OOOO000KKKKXX0K0000KKXXXXNNXXXXXXXXXXXXXXXXNNNNNNXXNNNNNNNNNNNNNNNWWWWNNNNNNNNNNNNNNNNNNNNXXXXXXXNXXXXNNNNNNNXXXXXXXXXXXXKKXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXNXXXXXXXXXKKKKKKKKKKK0000O:",
";dOKKKKKKKKXXXXXXXXKKKKKKXXXXXXXXXXXXXXXKKKKKKKKKXXKKKKKKKK0000KK000KXKKKK000KKKKXXXXXXXNNNNNNNXXNNXXNNNNNXXXNNNNNNNNNNNNXNNNNNNWNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXXNNNNNNXXXXXXKKKKKXXXXKXXXXXXKKXXXXXXXXXXXXXXXXXXXXXXXXXXXKKKXXXXXXXXKXXXXXXXKKKKKK0000O00c",
".:kKKKKKKKXXXXXXXXXXXXXXXXXXXXXXXXXKKKKK000KKKKKKKKKKKKKKXKKKK0OO0KKXKXXK000KKKXXXNXXXXNNXXNNNNNXNNXXXNNXXXXNNNXNNNXXXXXXXXNNNXNNNNNNNNNNNNNNNNNNNNNNXXXXXXXXNNNNNNXXXXXXXXXXXXXXXXXKKKKKKKKKKKKKXXXXXXXXXXXXXXXXXXNNNXXXXXXXXXKKKKKKKKKKKKKKKKK00OOO0x.",
".,lOKXXKKKXXXXXXXXXXXXXXXKKXXXXXXKKKKKKKKKKKKKKKKKKKKKKXXXKKK00K00KKXXXKKKKKKKKKXXKKXXXKKKXNXXNNN&XXXXXXXXXXXXXXXXXXXXNNNNNXXXXXXNXXNNNNNNNNNNNNNNXXXXXXXXXNNNXXXXXXXXXXXXXXXXXXXXXXKKKKKKKKKKKKKKKKKKKXXXXXXXXXXXXNXXXXXXXKKKKKKKKKK0KKKKK0000000000k'",
".,cx0KKKXXXXXXXXXXXXKKKKKKXXXXXKKKKKKKKKKKKKKKKKKKKKKKKXXXKKK00000KKXXKKXXNXK0KKKXKKXXKXNXXNNNXXXXXXXXXXNNNNNNXNXXNNNNNXXXXXNXXXXXXXXXXNNNNNXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXKKKKKKKKKKKKKKKKKKKKKXXXXKKKKKXXXXKKKKKKKKKKKKK000000000000000OOKk.",
";x0KKKKXXXXXXXXKKKKKKKKKKKKKKKKKKKKKKKKKK000KKK00KKKKKKKK00000000KXXXXXNXKK00KXXXXXXXXNNNNXXXXXXXXXXXXXXXXXXXNNXXXXNNNNNXXXXXXXXXXXXXXNNXXXXKKKKXXXXXXXXXXXXKXXXXXKXXXKXXXXKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK000OO00000KKKK0OO0Kl.",
".cxO0KKKKKXXXKKKKKKKKKKKKKKKK0000000000000000000KKKXNNNXXKK0000KXXXKK0KXXK00XXXXXXXXXXXXXXXKKKKKXXXXXXXXXXXXNNXXXXXXXXXXNNXXXKXXXKXXXXXXXXXKKKKKKKKKKXXXKKKXXXXXXXXXXXKKXXKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKXXKKKKKKKXXKKKKKKKKK0KKK0KKXK0OOKK:",
"..:dOKKKKKKKKKKKKKKKKKKKK000000000OOOO0XXNNNNNWWMMMMWWNXKKKKKKKKKKKKKXXKKXXKXNNXXXKXKKXXXKKKKKXXXXXXXXXXKKXXXXXXXKKKXXXXXXXKXXXKKKKKKXXXXXXXXKKKKKKKKKKKKXXXNXXXXXXXXXXXKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKXXXXXKKKKKXXKKKKKKK0OkO0d.",
".';ld0KKKKKK000000000000K000000O0XNWNNNNNNNWWWMMMMMWNXKKKKKKKKKKKKKKKKKXXXXNXXXXK0KKKKKKKKKXKKKXXXXKKKKKXKKXKKKXXKKKXXXXXXXXKKKKKXXXXXXXXKKKK000000KKXXXXXXXXXXXXXXXKKKKKKKKKXXKXXKXKKKKKKXXXXKKKKKKKKKXXKKKXXXXXXXKKKXXKKKXK0OOO0O:",
".,',cldkkkK0kkkOKXXXK000000000000000KKKXXXXNNNWWWNXKKKKKKKKKXKK000KKKXNXKXXKKKXKKXKKKKKKKKKKKKKKKKKXKKKKKKXKKKKXXNNXKKXXXXXXXXXNNXXXXXK0OOO0000KKKKKKXXXXXXXXXXXXXXXXXXXXXXXXXXKKKKKKKKXXXXXXXKKXXXXXKKXXXXXXXXKKXXXK000OOO0k;",
"...,'...:x0KK0000000000000000000KKKKKKKKKKXXKO0KKK0000KKXX0000KKKKKXXXXXXXXXXKKKKKKKKKKKKKKKKKKKKKKKKKKXXXXXKKKKKKXXXXNNXXXXXXKK00OO00000000KKKKXXXXXXXXXXXXXXXXXXXXXXXKKKKXKKKKKKKKKXXXXXXXXXXXKKXXXXXKKKKKKK00OO0Ol.",
"....'.'cdxkOO00KKKKKKKKKKKKKKKKKKKKOxO0kd:lKK0O00OO0KKK000KXK00KKKXNXXXXXXKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKXXKKKKKKXNXXXXXKKKKK00KKKKK0000KKKKKKKXXXXXXXXXXXXXKXXXXXKXXXXXKKKKKKKKXXXXXKKKXXXKKKXXKKKKKKKK00OO0x,",
"...       ....,;:clc:;::::::::c:;;::..,'',',ck0KKK00O0000KXXKK00KKKKKKKKKKXKKKK00KKKKK00000KKK00KKKKKKKKKKKKKXXKKKKKKXXXKKKKKKKKKKKKKKKKKKK00KKKKKKKKKKXXXKXXXXXXKKKKKKKKKKKKKKKKKKKXXXKKKKKKKKKKKKKK00000OOOKd.",
".'l0XK00000O0KXXXXKXXKKK00000KKKKKKKKKK00000000KK0KKKKKKKKKKKKXXXXKKKKKKKKXXXXXKKKKKKKKKKKKKKKKK0KKKKKKKKKKKKKKKKKKKKKK0K00000KKKKKKKKKXXXXKKKKKK000KKK0000OOOOOo.",
";ok0KKKK00KKKKKKXXKK0000KK0KXXXXKKKKKK000000KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKXXXKKKKKKKXKXXKKKKKKKK00KKKKKKK00K000000000000000K0KKKKKKKKKKKKKK0000000000K0OO00:",
".:ddox00000KK0KKKK0OO00K00KKKXXXXKKKK0000000000KKKKKKKKKKKKKKKKKKKKKXXKKKKKKKKKKKKKXXXNXKXXXKKKK00000KKK00KK00000000000000KKKKKKKKKKKKKK000000000000OO00d'",
"..;d00000OO00KK0O000000KKKKXXXKKKKKKKKK00K0000000KKKKK00KK0KKK0KKKXXKKKKKKKKKKKXXXXXXXKKKKKKKK00KKKK0000KK00000000000KKKKKKKXXKKK0000000KKK000OOOOKOl.",
"'dkxkOOOO0KKK0000000K0KKKKXXXXKKKKKKKK0000OOOOO0KKK000000000KKKKK00KKKKKKKKXXKKKKKKK0KKKKKKKXXKKKKKKKKKK000000K00KKKKKKXXXKKK00000000KK00OOOO0Od;",
"...:ldOO00KK0000000OO0KKXNNXKK00000KKK000OOOO00KKK00KKK000KKKK00000K0KK0KKKKKKKKK000KKKKKKKXKKKKKKKKKKKKKK0KKKKKKKKKKKKKKKKKK00000000OOOkOOkc.",
"'x0OO00KKK0OO0OO00KKKXXKKKKKK00KK00K0000OOO000000KK000K00000000K000KKKKK000000000KKKKKKKKKKK0000KKKXXKKK00KKKKKKKKKKKKKKKK00OO0OOOOO0Ox;.",
".dK0OOOO0KKKK00OO0K00000KKXXXXXKKK00KK0KK0OO00000000000000000000000000KK000000K0KKKKKK00K0KK00000000KKK00000KKKKKKKKKKKKKK0000OOOOOO0x:'",
".;cdO000000KKKK00000O000KXXKKKKK000KKKKKK00000000000000000KKKK000000KKKKKKKKKKKKKKKKKKKKKKK0000000000000000000KKKKKKKK0K00000OOO0KKd'",
"'o00000O00KK000000000KXK0KKKKK00KKKKK000KKKKKK0O00000000000KXXK0KKKKKKKXXXXKKKKKKKKKKKKK000000000000000000000KKKK00KK0000OO0kxc.",
".:lok0O0000K00000000000000KKKKKK000KKKKKKKKXX000000KKKKK00KKKKKKKKKKKKKXXXKKKK0KKKKKKK00000000000000000000000KK000KKK0000koc;.",
".oO000O000000OOO0OO00KXXK0000KKKKKKKKKKXXK000KKKKKKK000KKKKK0KKKKKKKXXXXKKK0KKKKK0000000000000000O00O000000000000OOkd, ..",
".'lk00000OOOOOOOOOOOO0000000KXXXXXKKKKKKKKK0KK0KKKKKKKKKKK0000000KKKXXXKKKKKXKK0000000000000000OOOOO000OOkOOOO0KOc. ..",
".;lx00OOOOOOO0OkkOOOO0O000KXXNNXK00KKKKKKKK0000KKKKKKKKK000000000KKKKKKKKKK000KKKKKKK0000OOOO00OOOkkkkkOO000Ol.  ....",
".;;:dOO00OkkOO00OkkkO00000KKXXXXKKKKKKKXXXXKK0KKKK000KKKKK000000000KKKKKKKK000KK00K000OOOkkkkkkkkkkOOOxl:,..    ,l:'",
".. .,ck00OkkkO0OOOOkO00000KKKKKKK00KKKXXXKKXXKKK0000000KK0000000000000000K00000K00OOOkOkkxxxxkOxoOk;..     .'..'.",
".,cdxkOOOOOOOO0000000OO00K0000KKKXXKKKKKKK0000KKK000000000000000000K0000KKK00OkkkkkkkkOxdl...   .......",
".,okOOOOOOOOOOOOOOOOO000000KXXKKKKKKKK00KKKKK00KK000000OOO000000OO0K00000OkkkkkOkdc.    ..,:,.",
"..,:lokO00OkkkkOOOOOkO0K00KKKKKKKKKK0O0KK0KXXNNKOOOOOOOOOOOOOOOOOkkkkkkkOO0O:'.   .':'.'.",
".coxkkkkxxxkOOkkOOOOO0KKKKKKKKK000000KKKKKOkO0OkkkOkkkOOkkkkkxxkOOxl;,..'......",
".';coxkOOkkkOOkkkkOOOOOO000O0000OOOOOOOOO00OOkkkkkOOOkxxkkkxl,,. .'',;.",
"':cdkOOOOOOkkOkkkkxkOkkkkOOkkkOkkkkOK0OOOkxxO000Okxoc;,,''...'.",
".::lloxkO00OOOkkkOOkkkkOkkkkkOK0OO0OOKKOO000xo:'. ;ol:.",
"'c:ckOkO000OOOOOOOOOOOOO0000OO00xol:;'......'.",
".,;;cdoldxdoc:;c:,,,,:ccl::;'....'..'.",
];

# So the ascii appears on the webpage from bottom to top
texts.reverse()

# How many arduinos do we expect to hear from?
# Arduino TX/RX01, Arduino TX/RX02, Arduino TX/RX03, Arduino TX/RX04, Arduino TX/RX05, Arduino TX/RX06
receivers = [0xF0F0F0F0C1]
transmitters = [0xF0F0F0F0C5]
t_indexes = ["0xF0F0F0F0C5"]
num_children = len(transmitters)

# Start the radio
radio.begin()

radio.setRetries(3, 5);
radio.enableDynamicPayloads();
radio.printDetails()

##########################################
# STATUS
#
# sending = 0 (when we select an image, transform to byte array and transmit to receiving children)
# receiving = 1 (while we wait to hear back from transmitting children)
# saving = 2 (we heard back from all transmitting children, now save to DB)
# Then go back to 'init'!

status = 0

# Get the time
millis = lambda: int(round(time.time() * 1000))

# Dict for saving received data from transmitting children arduinos
received_payloads = dict()
payload_index = 0
payload_size = 4

# Endpoint for display
url = 'https://weise7.org/plant-2-plant/save'
# url = 'http://192.168.2.1:3000/save'

##########################################
# DEFs
#
def select_text(index=0):
    return texts[index]

def save_images():
    for child in received_payloads:
        files = { 'file': ('image.bmp', io.BytesIO(received_payloads[child]), 'image/bmp') }
        r = requests.post(url, files=files)

def check_responses():
    # first check if the dictionary has entries for all transmitting children
    # print('length of received_payloads dict {} should == num_children {}'.format(len(received_payloads), num_children))
    if len(received_payloads) < num_children:
        return False

    # then check if each child has the correct number of entries to its list
    for child in received_payloads:
        # print('len(received_payloads[child])/4 {} should == transmission_id {}'.format(len(received_payloads[child])/4, transmission_id))
        # divide by four because we are adding batches of 4 packets per tranmission
        if len(received_payloads[child])/4 < transmission_id:
            return False

    print("responses are good!")
    return True

def handle_timeouts():
    # fill the spot in the file with whatever other chars so we can move on
    if len(received_payloads) < num_children:
        # print('missing a key!')

        tx_keys = received_payloads.keys()
        for t in t_indexes:
            if not t in tx_keys:
                # print('will create key {}'.format(t))
                received_payloads[t] = bytearray(b'__')
                # print(received_payloads)

    # then check if each child has the correct number of entries to its list
    for t in received_payloads:
        # divide by four because we are adding batches of 4 packets per tranmission
        if len(received_payloads[t])/4 < transmission_id:
            #print('{} was missing a packet!'.format(t))
            received_payloads[t].extend(b'__')
            #print(received_payloads[t])

def read_file_data(channel=0):
    if radio.available():
        while radio.available():
            p = radio.available_pipe()
            if (p[0] and p[1]):
                #print('# # # # # # # # # # # # # #\n')
                #print('p {}\n'.format(p))

                len = radio.getDynamicPayloadSize()
                file_payload = radio.read(len)

                key = t_indexes[p[1]-1]
                #print('key {}'.format(key))
                if key in received_payloads:
                    received_payloads[key].extend(file_payload)
                else:
                    received_payloads[key] = bytearray(file_payload)

                # print('Received payload {} on pipe {}\n'.format(file_payload, key));
                print('All saved payloads {}\n'.format(received_payloads));

##########################################
# INIT
#

send_payload = select_text(text_id)
max_payload_size = len(send_payload)
#print(send_payload)
print('max_payload_size {}, will require {} transmissions'.format(max_payload_size, max_payload_size/payload_size))

# forever loop
while 1:

    # sending data
    if status == 0:
        # First, stop listening so we can talk.
        radio.stopListening()

        # Send next chunk
        payload = send_payload[payload_index:payload_index+payload_size]

        print('Status 0: Sending {}'.format(payload))

        for n in range(0, num_children):
            # open the writing pipe with the address of a receiver child
            radio.openWritingPipe(receivers[n])
            result = radio.write(payload.encode('utf-8'))

            print('successful send to receiver child {}? {}'.format(receivers[n], result))

            if result:
                txNum += 1
                if (txNum >= num_children):
                    #print('Sent successfully to all receiving children.')
                    txNum = 0
                    status = 1
            else:
                print('TX failed')

    # receiving data
    elif status == 1:
        #print('Status 1: Waiting for data from transmitting children Arduinos\n')

        # Now we wait to get the data back from the sender Arduino
        radio.startListening()

        # Wait here until we have heard from everyone, or timeout
        started_waiting_at = millis()
        timeout = False

        while (not check_responses()) and (not timeout):
            for n in range(0, num_children):
                # open the reading pipe with the address of a transmitting child
                radio.openReadingPipe(n+1, transmitters[n])
                # Read the file data and save it to our dict once it shows up
                read_file_data()

                if (millis() - started_waiting_at) > 200:
                    timeout = True

        # Describe the results
        if timeout:
            # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')
            # print('Fail - Response timed out. Handling and then moving on.')

            handle_timeouts()
            timeout = False

            # print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n')
        else:
            #print('Success - Moving onto transmission {}'.format(transmission_id))
            # Start a new round of transmission
            transmission_id += 1

            # Step through the payload...
            payload_index += payload_size

            # If we have stepped through the entire payload, save to database
            if payload_index >= max_payload_size:
                status = 2
            else:
                # otherwise, set status back to 0 so we transmit again
                status = 0

    # saving data
    elif status == 2:
        # print('Status 2: Received all image data back, saving image locally and to DB\n')

        # Now we save it to our web app endpoint
        save_images()

        # reset everything:
	if text_id == len(texts)-1:
            text_id = 0
	else:
            text_id += 1
        send_payload = select_text(text_id)
        max_payload_size = len(send_payload)
        #print('New max_payload_size {}'.format(max_payload_size))
        received_payloads = dict()
        payload_index = 0
        transmission_id = 1
        txNum = 0
        status = 0

    # debugging
    elif status == 3:
        continue
        # test status, print nothing, go back to beginning of loop

    # error; status equals something strange
    else:
        print('Status error! {}\n'.format(status))

    time.sleep(0.1)
