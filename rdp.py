###########################################################################
#
# CSC 361 P2 - Reliable Datagram Protocol (RDP) Tranceiver
# Author: Bryan Quan
# Date: Feb 2024
# Desciption: Combined sender and receiver for data packets
#
###########################################################################

import socket
import select
import sys
import re
import os

class rdp_sender:
    # closed -> syn_sent -> open -> fin_sent -> closed
    state = "closed"
    
    def open(self):
        # write SYN rdp packet into snd_buf
        self.state = syn_sent
    def close(self):
        # write FIN packet to snd_buf
        self.state = fin_sent
    def check_timeout(self):
        timeout = 0
        if self.state != closed and timeout:
            print("rewrite the rdp packets into snd_buf")
    def getstate(self):
        return self.state

class rdp_receiver:
    # closed -> syn_sent -> open -> fin_sent -> closed
    state = "closed"
    
    def open(self):
        # write SYN rdp packet into snd_buf
        self.state = syn_sent
    def close(self):
        # write FIN packet to snd_buf
        self.state = fin_sent
    def check_timeout(self):
        timeout = 0
        if self.state != closed and timeout:
            print("rewrite the rdp packets into snd_buf")
    def getstate(self):
        return self.state
    
###########################################################################
#
# Functions  Go-back N: page 251
#
###########################################################################

def send(self):
    
    # RDP Error Control
    if self.state == open:
        pass
#         for seq in [snd_next, snd_una + window]
#             print("write rdp packet with swq into snd_buf")

            
def rcv_ack(self):
    if self.state == syn_sent:
        if ack_num is correct:
            self.state = open
    if self.state == open:
        duplicate_received = 0
        if duplicate_received == 3:
            print("rewrite the rdp packets into snd_buf")
        if ack_num is correct:
            print("move the sliding window")
            print("write the available window of DAT rdp packets into snd_buf")
#         if all data has been sent:
        if true:
            self.close()
    if self.state == fin_sent:
        if ack_num is correct:
            self.state = closed
             
def rcv_data(self):
    
    if self.state == open:
        rdp_pacl = 0
        if data.seq < rcv_exp:
            print("drop packet")
        if data.seq > rcv_exp:
            print("put the rdp with seq into a buffer data_bug")
            return rdp_pack
        if data.seq == rcv_exp:
            #check data_buf and update rcv_exp
            
            #return an ack rdp packet
            return
        
###########################################################################
# Init
###########################################################################

# init UDP socket
# udp_sock = socket.socket()

# udp port (hardcode this)
port = 8888


# create sender/receiver instances
rdp_sender = rdp_sender()
rdp_receiver = rdp_receiver()

###########################################################################
# Main Loop
###########################################################################

while ((rdp_sender.getstate() != "closed") or (rdp_receiver.getstate() != "closed")):
    
    readable, writable, exceptional = select.select([udp_sock],[udp_sock],[udp_sock],timeout)
    if udp_sock in readable:
        # receive data and append it into rcv_buf
        print("hello")
#         if the message in rcv_buf is complete (detect a new line):
        if true:
         # extract the message from rcv_buf
         # split the message into RDP packets
            for packet in rcv_buf:
#                 if RDP packet is ACK:
                if packet:
                    rdp_sender.rcv_ack(message)
                else:
                    rdp_receiver.rcv_data(message)
                    
    if udp_sock in writable:
        bytes_sent = udp_sock.sendto(snd_buf, ECHO_SRV)
        # remove the bytes already sent from snd_buf
    
    rdp_sender.check_timeout()