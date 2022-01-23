import subprocess

class VideoResizer:
    def convert(src, target, res):
        subprocess.call('ffmpeg -i "{}" -s {}x{} -c:a copy {} -y'.format(src, res[0], res[1], target), shell=True)