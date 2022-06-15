import numpy as np
from PIL import Image
import time
from tqdm import tqdm
from scipy.interpolate import PchipInterpolator
import argparse
import json
import random
from numba import njit


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--centre',
                        help="centre of the image on the plane. give in the format"
                             "x y")
    parser.add_argument("-cs", "--centre-string")
    parser.add_argument('-z', '--zoom', type=float)
    parser.add_argument('-r', '--resolution', type=str,
                        choices=["ultra", "high", "med", "low"], default="med")
    parser.add_argument('-a', '--aspect-ratio', type=str,
                        help="give in the format x:y", default="16:9")
    parser.add_argument('-i', '--max-iters', type=int, default=1000)
    parser.add_argument('-b', '--bound', type=int, default=500)
    parser.add_argument('-sc', '--save-config', type=str,
                        help='name of image you want to save')
    parser.add_argument('-sd', '--save-data', action='store_true')
    parser.add_argument('-ld', '--load-data')
    parser.add_argument('-p', '--pallete', default='warm')

    args = parser.parse_args()

    config = json.load(open('configs.json'))
    pallete = config['palletes'][args.pallete]
    args.vals = pallete['vals']
    args.colours = pallete['colours']

    if args.centre is None or args.zoom is None:
        if args.centre_string is None:
            image_index = random.randint(0, len(config['images'].values()) - 1)
            args.centre = args.centre or [*config['images'].values()][image_index]['centre']
            args.zoom = args.zoom or [*config['images'].values()][image_index]['zoom']
            args.centre_string = [*config['images'].keys()][image_index]
        else:
            args.centre = config['images'][args.centre_string]['centre']
            args.zoom = config['images'][args.centre_string]['zoom']
    else:
        args.centre = tuple([float(point) for point in args.centre.split()])

    # purely for naming purposes of the image
    if args.centre_string is None:
        args.centre_string = "custom"

    args.aspect_ratio = tuple([int(num)
                               for num in args.aspect_ratio.split(':')])

    resolution_dict = {
        'ultra': 240,
        'high': 120,
        'med': 60,
        'low': 20
    }
    args.resolution = tuple(
        [num * resolution_dict[args.resolution] for num in args.aspect_ratio])

    if args.save_config is not None:
        # TODO: check for duplicates before saving
        new_image = {'centre': args.centre, 'zoom': args.zoom}
        config['images'][args.save_config] = new_image
        json.dump(config, open('configs.json', 'w'))
        print("saved image. exiting...")
        exit(0)

    return args


def save_image(image, args):
    curr_time = time.strftime('%H:%M:%S', time.localtime())
    if args.load_data is not None:
        image.save(f'{args.pallete}-{args.load_data[:-4]}-{curr_time}.png')
    else:
        image.save(f'{args.pallete}-{args.centre_string}-{curr_time}.png')


@njit
def jit_get_iter_counts(x_axis, y_axis, resolution, max_iters, bound):
    iteration_counts = np.zeros(resolution, dtype=np.int16)
    for i, x in enumerate(x_axis):
        for j, y in enumerate(y_axis):
            z = c = complex(x, y)
            iters = 0
            for iters in range(max_iters):
                z = z ** 2 + c
                if abs(z) > bound:
                    break
            iteration_counts[i, j] = iters
    return iteration_counts


@njit
def jit_get_cumulutive_pp(iteration_counts):
    num_iters_pp = np.zeros(iteration_counts.max() + 1, dtype=np.int32)
    for row in iteration_counts:
        for count in row:
            num_iters_pp[count] += 1
    return num_iters_pp


def main():
    args = get_args()
    # TODO: comment it up
    cs = PchipInterpolator(args.vals, args.colours)

    x_axis = np.linspace(args.centre[0] - args.aspect_ratio[0] / args.zoom,
                         args.centre[0] + args.aspect_ratio[0] / args.zoom,
                         args.resolution[0])
    y_axis = np.linspace(args.centre[1] + args.aspect_ratio[1] / args.zoom,
                         args.centre[1] - args.aspect_ratio[1] / args.zoom,
                         args.resolution[1])

    if args.load_data is not None:
        hue_array = np.load(f'data/{args.load_data}')
        image = Image.new(mode="RGB", size=hue_array.shape)
        for i, row in tqdm(enumerate(hue_array)):
            for j, num in enumerate(row):
                hue = cs(num)
                image.putpixel((i, j), tuple([int(num) for num in hue]))
        save_image(image, args)
        return
    start = time.perf_counter()
    image = Image.new(mode="RGB", size=args.resolution)

    iter_start = time.perf_counter()
    iteration_counts = jit_get_iter_counts(x_axis, y_axis, args.resolution, args.max_iters, args.bound)
    num_iters_pp = jit_get_cumulutive_pp(iteration_counts)
    print(f"total iter time: {time.perf_counter() - iter_start}")

    total = args.resolution[0] * args.resolution[1]

    if args.save_data:
        hue_array = np.zeros_like(iteration_counts).astype(float)
    for i, row in tqdm(enumerate(iteration_counts)):
        for j, count in enumerate(row):
            hue = cs(num_iters_pp[:count + 1].sum() / total)
            hue = [int(i) for i in hue]
            if args.save_data:
                hue_array[i][j] = num_iters_pp[:count + 1].sum() / total
            image.putpixel((i, j), tuple(hue))

    save_image(image, args)
    if args.save_data:
        np.save(f'data/{args.centre_string}', hue_array)
    print(time.perf_counter() - start)


if __name__ == '__main__':
    main()
