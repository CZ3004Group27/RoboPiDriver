
from bluetooth import *

class Server:
    def __init__(self):
        server_sock = BluetoothSocket(RFCOMM)
        server_sock.bind(("", PORT_ANY))
        server_sock.listen(1)

        port = server_sock.getsockname()[1]

        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

        advertise_service(server_sock, "SampleServer",
                          service_id=uuid,
                          service_classes=[uuid, SERIAL_PORT_CLASS],
                          profiles=[SERIAL_PORT_PROFILE],
                          #                   protocols = [ OBEX_UUID ]
                          )

        print("Waiting for connection on RFCOMM channel %d" % port)

        client_sock, client_info = server_sock.accept()
        #TODO restart socket if closed
        while True:
            print("Accepted connection from ", client_info)
            data = client_sock.recv(2048)
            if len(data) == 0:
                continue
            else:
                # self.parse_android_message(data)
                # Send command to main thread
                print("received [%s]" % data)
                print("sending response")
                client_sock.send(b"response hello")

        print("stopping!")
        client_sock.close()
        server_sock.close()


server = Server()