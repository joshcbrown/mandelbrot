import argparse
import json
import random


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

    config = json.load(open('../configs.json'))
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
        json.dump(config, open('../configs.json', 'w'))
        print("saved image. exiting...")
        exit(0)

    return args
