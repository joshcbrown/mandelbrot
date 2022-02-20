import numpy as np
from PIL import Image
import time
from tqdm import tqdm
from scipy.interpolate import PchipInterpolator
import argparse
import json
import random


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--centre', 
                        help="centre of the image on the plane. give in the format"
                             "x y", )
    parser.add_argument('-z', '--zoom', type=float)
    parser.add_argument('-r', '--resolution', type=str, choices=["high", "med", "low"], default="med")
    parser.add_argument('-a', '--aspect-ratio', type=str,
                        help="give in the format x:y", default="16:9")
    parser.add_argument('-i', '--max-iters', type=int, default=300)
    parser.add_argument('-b', '--bound', type=int, default=500)
    parser.add_argument('-s', '--save-config', action='store_true')

    args = parser.parse_args()
    if args.centre is None or args.zoom is None:
        asdf = json.load(open('configs.json'))
        image_index = random.randint(0, len(asdf['images']) - 1)
        args.centre = asdf['images'][image_index]['centre']
        args.zoom = asdf['images'][image_index]['zoom']
    else:
        args.centre = tuple([float(point) for point in args.centre.split()])

    args.aspect_ratio = tuple([int(num) for num in args.aspect_ratio.split(':')])

    resolution_dict = {
        'high': 120,
        'med': 60,
        'low': 20
    }
    args.resolution = tuple([num * resolution_dict[args.resolution] for num in args.aspect_ratio])
    
    if args.save_config:
        asdf = json.load(open('configs.json'))
        new_image = {'centre': args.centre, 'zoom': args.zoom}
        asdf['images'].append(new_image)
        with open('configs.json', 'w') as f:
            json.dump(asdf, f)

    return args

def iter_count(c: complex, args: argparse.ArgumentParser) -> int:
    z = c
    for i in range(args.max_iters):
        z = z ** 2 + c
        if abs(z) > args.bound:
            return i
    return args.max_iters

def main():
    args = get_args()

    VALS = (0.05, 0.1, 0.3, 0.6, 0.9, 1)
    COLOURS = ((0, 18, 25), (0, 18, 25), (10, 147, 150), (233, 216, 166), (174, 32, 18), (0, 18, 25))
    cs = PchipInterpolator(VALS, COLOURS)

    x_axis = np.linspace(args.centre[0] - args.aspect_ratio[0]/args.zoom, 
                         args.centre[0] + args.aspect_ratio[0]/args.zoom, 
                         args.resolution[0])
    y_axis = np.linspace(args.centre[1] + args.aspect_ratio[1]/args.zoom, 
                         args.centre[1] - args.aspect_ratio[1]/args.zoom, 
                         args.resolution[1])
    image = Image.new(mode="RGB", size=args.resolution)

    iteration_counts = np.zeros(args.resolution).astype(int)
    for i, x in tqdm(enumerate(x_axis)):
        for j, y in enumerate(y_axis):
            iteration_counts[i][j] = iter_count(complex(x, y), args)

    num_iters_pp = np.zeros(iteration_counts.max() + 1).astype(int)
    for row in iteration_counts:
        for count in row:
            num_iters_pp[count] += 1

    total = args.resolution[0] * args.resolution[1]
    for i, row in enumerate(iteration_counts):
        for j, count in enumerate(row):
            hue = cs(num_iters_pp[:count + 1].sum() / total)
            hue = [int(i) for i in hue]
            image.putpixel((i, j), tuple(hue))

    curr_time = time.strftime('%H:%M:%S', time.localtime())
    image.save(f'{curr_time}.png')

if __name__ == '__main__':
    main()