import numpy as np
from PIL import Image
import time
from tqdm import tqdm
from mandelbrot import get_iter_counts, get_cumulative_pp
from linear_interp import LinearInterpolator
from options import get_args


def save_image(image, args):
    curr_time = time.strftime('%H:%M:%S', time.localtime())
    if args.load_data is not None:
        image.save(f'{args.pallete}-{args.load_data[:-4]}-{curr_time}.png')
    else:
        image.save(f'{args.pallete}-{args.centre_string}-{curr_time}.png')


def handle_loading_data(args, cs):
    hue_array = np.load(f'../data/{args.load_data}')
    image = Image.new(mode="RGB", size=hue_array.shape)
    for i, row in tqdm(enumerate(hue_array)):
        for j, num in enumerate(row):
            hue = cs(num)
            image.putpixel((i, j), tuple([int(num) for num in hue]))
    save_image(image, args)


def generate_image(args, iteration_counts, num_iters_pp, total, cs):
    image = Image.new(mode="RGB", size=args.resolution)
    if args.save_data:
        hue_array = np.zeros_like(iteration_counts).astype(float)
    for i, row in tqdm(enumerate(iteration_counts)):
        for j, count in enumerate(row):
            hue = (cs(num_iters_pp[:count + 1].sum() / total)).astype(int)
            if args.save_data:
                hue_array[i, j] = num_iters_pp[:count + 1].sum() / total
            image.putpixel((i, j), tuple(hue))
    if args.save_data:
        np.save(f'../data/{args.centre_string}', hue_array)
    return image


def main():
    args = get_args()

    cs = LinearInterpolator(args.vals, args.colours)
    if args.load_data is not None:
        handle_loading_data(args, cs)
        return

    x_axis = np.linspace(args.centre[0] - args.aspect_ratio[0] / args.zoom,
                         args.centre[0] + args.aspect_ratio[0] / args.zoom,
                         args.resolution[0])
    y_axis = np.linspace(args.centre[1] + args.aspect_ratio[1] / args.zoom,
                         args.centre[1] - args.aspect_ratio[1] / args.zoom,
                         args.resolution[1])
    start = time.perf_counter()

    iteration_counts = get_iter_counts(x_axis, y_axis, args.resolution, args.max_iters, args.bound)
    num_iters_pp = get_cumulative_pp(iteration_counts)
    print(f"total iter time: {time.perf_counter() - start}")

    total = args.resolution[0] * args.resolution[1]
    image = generate_image(args, iteration_counts, num_iters_pp, total, cs)
    save_image(image, args)
    print("total time: ", time.perf_counter() - start)


if __name__ == '__main__':
    main()
