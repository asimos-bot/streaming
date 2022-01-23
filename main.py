from streaming.server import StreamingServer
from service.manager import ServiceManager
from multiprocessing import Process

def parse_loglevel_from_cli(args):
    for arg in sys.argv:
        if(arg.startswith("--log=")):
            return arg.split('=')[1]
    return "INFO" # default

if __name__ == "__main__":
    import sys
    loglevel = parse_loglevel_from_cli(sys.argv)
    service_manager = Process(target=ServiceManager, args=(5000,))
    streaming_server = Process(target=StreamingServer, args=(6000, ('127.0.0.1', 5000), loglevel))
    service_manager.start()
    streaming_server.start()
    service_manager.join()
    streaming_server.join()
