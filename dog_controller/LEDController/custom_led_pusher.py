import socket
UDP_IP = "192.168.123.13"
UDP_PORT = 8889

# convert hex to decimal
DATA = "eeeeeeee"
ZERO = "88888888"
EMPTY = "00000000"
colors = [
    DATA, ZERO, ZERO,  #1
    DATA, ZERO, ZERO,  #2
    DATA, ZERO, ZERO,  #3
    DATA, ZERO, ZERO,  #4
    DATA, ZERO, ZERO,  #5
    DATA, ZERO, ZERO,  #6
    DATA, ZERO, ZERO,  #7
    DATA, ZERO, ZERO,  #8
    DATA, ZERO, ZERO,  #9
    DATA, ZERO, ZERO,  #10
    DATA, ZERO, ZERO,  #11
    DATA, ZERO, ZERO,  #12
]
data = ""
for color in colors:
    data += color
# send via udp
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(bytes.fromhex(data), (UDP_IP, UDP_PORT))
