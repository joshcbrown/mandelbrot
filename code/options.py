import argparse
import json
import random


def get_args():
    config = json.load(open('../configs.json'))
    palletes = config["palletes"].keys()
    centre_strings = config["images"].keys()

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--centre',
                        help="centre of the image on the plane. give in the format"
                             "x y")
    parser.add_argument("-cs", "--centre-string", help=f"allowed choices: {', '.join(centre_strings)}")
    parser.add_argument('-z', '--zoom', type=float, default=8)
    parser.add_argument('-r', '--resolution', type=str,
                        choices=["ultra", "high", "med", "low"], default="med")
    parser.add_argument('-a', '--aspect-ratio', type=str,
                        help="give in the format x:y", default="16:9")
    parser.add_argument('-i', '--max-iters', type=int, default=1000)
    parser.add_argument('-b', '--bound', type=int, default=2)
    parser.add_argument('-sc', '--save-config', type=str,
                        help='name of image you want to save')
    parser.add_argument('-sd', '--save-data', action='store_true')
    parser.add_argument('-ld', '--load-data')
    parser.add_argument('-p', '--pallete', help=f"allowed choices: {', '.join(palletes)}")
    parser.add_argument("-si", "--save-image", action="store_true", default=False)
    parser.add_argument("-g", "--gif", type=int, default=0)
    parser.add_argument("-n", "--number", type=int, default=1)
    parser.add_argument("-sp", "--splits", type=int, default=40)

    args = parser.parse_args()

    if args.pallete:
        pallete = config['palletes'][args.pallete]
        args.colours = pallete['colours']
        if "weights" in pallete.keys():
            args.weights = pallete["weights"]
        else:
            args.weights = [1 / len(args.colours)] * len(args.colours)

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
        with open("../configs.json", "w") as file:
            json.dump(config, file, indent=4, sort_keys=True)
        print("saved image. exiting...")
        exit(0)

    return args
