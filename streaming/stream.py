import user

class Stream():

    def __init__(self, video):
        self.video = video
        # self.__owner = owner

    # @property
    # def owner(self):
    #     return self.__owner
    # @owner.setter
    # def owner(self, value):
    #     raise Exception("Stream.owner is supposed to be a constant value!")

    def close(self):
        self.video.video_is_running = False
