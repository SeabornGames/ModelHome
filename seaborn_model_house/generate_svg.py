import os
import sys
from argparse import ArgumentParser

from seaborn_model_house.diagram import Diagram
from seaborn_model_house.wall_table import WallTable


def main(cli_args=sys.argv[1:]):
    args = parse_args(cli_args)

    diagram = Diagram(args.diagram_file) if args.diagram_file else None
    wall_table = WallTable(wall_file=args.wall_file) if args.wall_file else None


def parse_args(cli_args):
    parser = ArgumentParser(description='The layout.model_home will'
                                        ' create/update a diagram and wall file'
                                        ' as inputs to the mode_home generator')
    parser.add_argument('--diagram-file', '-d', default=None,
                        help='path to the input diagram-file.  If not'
                             ' specified then the floors will not be created.')
    parser.add_argument('--wall-file', '-w', default=None,
                        help='path to the wall-file which is a seaborn_table'
                             ' file defining the wall, door, and window'
                             ' height.  If not specified then the walls will'
                             ' not be created.')
    parser.add_argument('--wall-height', type=int, default=None,
                        help='default height in feet of the walls if not'
                             ' not specified in the wall-file.')
    parser.add_argument('--window-bottom', type=int, default=None,
                        help='default height in feet of the walls if not'
                             ' not specified in the wall-file.')
    parser.add_argument('--window-top', type=int, default=None,
                        help='default height in feet of the top of the window'
                             ' if not specified in the wall-file.')
    parser.add_argument('--door-height', type=int, default=None,
                        help='default height in feet of the door if not'
                             ' specified in the wall-file.')
    parser.add_argument('--output-folder', default=None,
                        help='folder to put the room svg files.'
                             ' Defaults to the folder of the --diagram-file '
                             ' plus ``rooms``')
    args = parser.parse_args(cli_args)

    if args.diagram_file is None and args.wall_file is None:
        print('--diagram-file or --wall-file must be specified')
        sys.exit(1)

    if args.output_folder is None:
        if args.diagram_file:
            args.output_folder = os.path.join(
                os.path.dirname(args.diagram_file), 'rooms')
        else:
            args.output_folder = os.path.join(
                os.path.dirname(args.wall_file), 'rooms')
    if not os.path.exists(args.output_folder):
        os.mkdir(args.output_folder)
    return args


if __name__ == '__main__':
    main()