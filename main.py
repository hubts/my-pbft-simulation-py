import bcpeer
import bcclient
import multiprocessing

def __gen_client(ip, port):
    client = bcclient.Bcclient(ip=ip, port=port, debug=1)
    client.main_loop()

def __gen_bcpeer(ip, port):
    bcpeer_i = bcpeer.Bcpeer(ip=ip, port=port, debug=1)
    bcpeer_i.main_loop()

if __name__ == "__main__" :
    for port in range(6230, 6234):
        p = multiprocessing.Process(
            target=__gen_bcpeer, 
            args=("127.0.0.1", port)
        )
        p.start()
    c = multiprocessing.Process(
        target=__gen_client,
        args=("127.0.0.1", 7250)
    )
    c.start()
