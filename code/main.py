import numpy as np
from PIL import Image
import time
from tqdm import tqdm
from mandelbrot import get_iter_counts
from linear_interp import LinearInterpolator, RandomLinearInterpolator, PaletteLinearInterpolator
from options import get_args
from tqdm import trange
import imageio
import glob


def save_image(image, args):
    curr_time = time.strftime('%H:%M:%S', time.localtime())
    if args.load_data is not None:
        image.save(f'{args.palette}-{args.load_data[:-4]}-{curr_time}.png')
    else:
        image.save(
            f'{args.palette}-{args.centre_string}-{curr_time}-{args.zoom}.png')


def handle_loading_data(args, cs):
    hue_array = np.load(f'../data/{args.load_data}')
    image = Image.new(mode="RGB", size=hue_array.shape)
    for i, row in tqdm(enumerate(hue_array)):
        for j, num in enumerate(row):
            hue = cs(num)
            image.putpixel((i, j), tuple([int(num) for num in hue]))
    save_image(image, args)


def generate_image(args, iteration_counts, total, cs):
    image = Image.new(mode="RGB", size=args.resolution)
    if args.save_data:
        hue_array = np.zeros_like(iteration_counts).astype(float)
    for i, row in tqdm(enumerate(iteration_counts)):
        for j, count in enumerate(row):
            hue = (cs(iteration_counts[i][j])).astype(int)
            if args.save_data:
                hue_array[i, j] = iteration_counts[i][j]
            image.putpixel((i, j), tuple(hue))
    if args.save_data:
        np.save(f'../data/{args.centre_string}', hue_array)
    return image


def to_save_or_not_to_save(image, args):
    if args.save_image:
        print(args.save_image)
        return args.save_image
    image.show()
    while True:
        if (save := input("save image? (y/n)").lower()) == "y":
            return True
        elif save == "n":
            return False
        print("invalid input ", save)


def plot_image(args, cs):
    x_axis = np.linspace(args.centre[0] - args.aspect_ratio[0] / args.zoom,
                         args.centre[0] + args.aspect_ratio[0] / args.zoom,
                         args.resolution[0])
    y_axis = np.linspace(args.centre[1] + args.aspect_ratio[1] / args.zoom,
                         args.centre[1] - args.aspect_ratio[1] / args.zoom,
                         args.resolution[1])
    start = time.perf_counter()

    iteration_counts = get_iter_counts(
        x_axis, y_axis, args.resolution, args.max_iters, args.bound)
    print(f"total iter time: {time.perf_counter() - start}")
    iteration_counts = iteration_counts / args.max_iters

    total = args.resolution[0] * args.resolution[1]
    image = generate_image(args, iteration_counts, total, cs)

    print("total time: ", time.perf_counter() - start)

    save = to_save_or_not_to_save(image, args)
    if save:
        save_image(image, args)


def get_palette(args):
    if args.palette == "random":
        return RandomLinearInterpolator(args.splits)
    return PaletteLinearInterpolator(args.colours, args.weights, args.splits)


def main(args):
    if args.load_data is not None:
        handle_loading_data(args, cs)
        return

    if args.gif == 0:
        for _ in range(args.number):
            cs = get_palette(args)
            plot_image(args, cs)
        return
    cs = get_palette(args)
    zoom = 4
    args.save_image = True
    for _ in trange(args.gif):
        zoom *= 1.25
        args.zoom = zoom
        plot_image(args, cs)

    images = []
    for filename in sorted(glob.glob("*.png")):
        images.append(imageio.imread(filename))
    imageio.mimsave("video2.gif", images)


if __name__ == '__main__':
    main(get_args())
