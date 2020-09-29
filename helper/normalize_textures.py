import glob
import os
import subprocess
import sys

from PIL import Image


def main():
    files = glob.glob(os.path.join(sys.argv[1], '*.png'))
    for filename in files:
        with Image.open(filename) as image:
            width, height = image.size
            if width < 128 or height < 128:
                subprocess.call(['ffmpeg', '-i', filename, '-vf', 'scale=128:128', '-sws_flags', 'neighbor', '-pix_fmt', 'rgba', '-y',
                                    filename])
                pass
            elif width > 128 or height > 128:
                subprocess.call(['ffmpeg', '-i', filename, '-vf', 'scale=128:128', '-pix_fmt', 'rgba', '-y',
                                    filename])
                pass

main()