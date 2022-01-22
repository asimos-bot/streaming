# from streaming.streaming_server import StreamingServer
# from service_manager import ServiceManager
# 
# def parse_loglevel_from_cli(args):
#     for arg in sys.argv:
#         if(arg.startswith("--log=")):
#             return arg.split('=')[1]
#     return "INFO" # default
# 
# if __name__ == "__main__":
#     import sys
#     loglevel = parse_loglevel_from_cli(sys.argv)
#     service_manager = ServiceManager(5000)
#     streaming_server = StreamingServer(6000, loglevel)
# 