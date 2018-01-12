import socket
import argparse

def get_local_ip(opt):
    ip = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((opt.connect_ip, 80))
        ip = s.getsockname()[0]
    except:
        print('ip get error')
    finally:
        s.close()
    return ip


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--connect_ip', type=str, default="10.3.9.4",
                        help='connect_ip')
    return parser.parse_args()


if __name__ == "__main__":
    opt = parse_opt()
    ip = get_local_ip(opt)
    print(ip)