import ffmpeg
import sys
import argparse

parser = argparse.ArgumentParser(description='Convert video')
parser.add_argument('in_filename', help='Input filename')
parser.add_argument('out_filename', help='Output filename')

def convert(in_filename:str, out_filename:str):
    try:
        stream = ffmpeg.input(in_filename)
        stream = ffmpeg.hflip(stream)
        stream = ffmpeg.output(stream, "output/"+out_filename)
        ffmpeg.run(stream)
    except ffmpeg.Error as e:
        print(e.stderr, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    args = parser.parse_args()
    convert(args.in_filename,args.out_filename)