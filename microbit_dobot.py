import microbit
import struct

# for checksum
def inv2(x):
    return (((x & 0xFF) ^ 0xFF) + 1) & 0xFF

# create DOBOT Protocol Packet
def pac(id, rw, q, payload):
    head = [0xAA, 0xAA, (len(payload) + 2) & 0xFF]
    body = [id, (0x01 if (rw != 0) else 0x00) | (0x02 if (q != 0) else 0x00)] + payload
    sum = 0
    for i in body[:]:
        sum += i
    body.append(inv2(sum & 0xFF))
    return bytearray(head + body)

# Byte[] to 4Bytes Float
def TPDToFloat(x):
    x = reversed(x)
    f = struct.unpack(">f", bytearray(x))
    return f[0]

# Float to Byte[]
def FloatToTPD4(f):
    f = struct.pack(">f", (f))
    l = list(f)
    l.reverse()
    return l

# Create X,Y,Z,R Packet
def CreatePTPPkt(cmdtype, x, y, z, r):
    return [cmdtype] + FloatToTPD4(x) + FloatToTPD4(y) + FloatToTPD4(z) + FloatToTPD4(r)

microbit.pin0.set_pull(microbit.pin0.PULL_UP)
microbit.pin1.set_pull(microbit.pin1.PULL_UP)
microbit.pin2.set_pull(microbit.pin2.PULL_UP)
microbit.uart.init(baudrate=115200, tx=microbit.pin1, rx=None)
microbit.sleep(50)

microbit.display.show("*")
while True:
    readpin0 = microbit.pin0.read_digital()
    readpin2 = microbit.pin2.read_digital()
    # if Pressed AB => End and go to REPL
    if microbit.button_a.is_pressed() and microbit.button_b.is_pressed():
        microbit.uart.init(baudrate=115200)
        microbit.display.show("E")
        break
    elif microbit.button_a.is_pressed():
        microbit.display.show("A")
        # CLEAR ALARM (Command=20, not 21 !!!)
        microbit.uart.write(pac(20, 1, 0, []))
        microbit.sleep(100)
        # GOTO HOME (Command=31)
        microbit.uart.write(pac(31, 1, 0, [0, 0, 0, 0]))
    elif microbit.button_b.is_pressed():
        # Z INC -5.0mm (Command=84)
        microbit.display.show("B")
        microbit.uart.write(pac(84,1,0,CreatePTPPkt(8,0,0,-5,0)))
    elif readpin0 == 0:
        microbit.display.show("0")
        # CLEAR ALARM (Command=20, not 21 !!!)
        microbit.uart.write(pac(20, 1, 0, []))
        microbit.sleep(100)
        # GOTO HOME (Command=31)
        microbit.uart.write(pac(31, 1, 0, [0, 0, 0, 0]))
    elif readpin2 == 0:
        # Z INC +5.0mm (Command=84)
        microbit.display.show("2")
        microbit.uart.write(pac(84,1,0,CreatePTPPkt(8,0,0,5,0)))
    microbit.sleep(100)
