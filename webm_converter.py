import subprocess
import os

class Converter:
    def __init__(self):
        pass
    def convert(self, filename):
        dir_ = os.path.dirname(os.path.realpath(__file__))
        inpath = dir_ + "/input/" + filename
        command = "ffmpeg  -i {}  -b:v 0  -crf 30 -y -pass 1  -an -f webm -y /dev/null".format(inpath)
        if subprocess.run(command, shell = True).returncode != 0:
            print("Oops")
            raise Exception("fuck")
        outpath = dir_ + "/output/" + filename.replace("mp4", "webm")
        command = "ffmpeg  -i {}  -b:v 0  -crf 30 -y -pass 2  {}".format(inpath, outpath)
        if subprocess.run(command, shell = True).returncode != 0:
            print("Oops")
            raise Exception("fuck")
        return outpath

