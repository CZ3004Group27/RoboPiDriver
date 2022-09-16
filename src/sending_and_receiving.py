def send_message_with_size(conn, data):
    number_of_bytes = len(data)
    packet_length = struct.pack("!I", number_of_bytes)
    packet_length += data
    conn.sendall(packet_length)
def receive_message_with_size(conn):
    try:
        data = conn.recv(4)
        if len(data) == 0:
            return None
        else:
            number_of_bytes = struct.unpack("!I", data)[0]
            received_packets = b''
            bytes_to_receive = number_of_bytes
            while len(received_packets) < number_of_bytes:
                packet = conn.recv(bytes_to_receive)
                bytes_to_receive -= len(packet)
                received_packets += packet
            return received_packets
    except socket.timeout:
        return None
    except:
        return None