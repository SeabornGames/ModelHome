import os
import sys
from argparse import ArgumentParser
from shutil import copyfile

from seaborn_model_house.diagram import Diagram
from seaborn_model_house.wall_table import WallTable


def main(cli_args=sys.argv[1:]):
    args = parse_args(cli_args)
    backup_files([args.diagram_file, args.wall_file], args.backup_folder)

    diagram = Diagram(args.input_file, args.checker, args.width, args.height)
    if args.remove_objects:
        diagram.remove_objects()

    if args.input_file:
        for highlight in (args.highlight_room or []):
            for room in diagram.rooms + diagram.objects:
                if room.name == highlight:
                    room.highlight(diagram)
        if not args.remove_names:
            diagram.add_names_to_grid()
        diagram.add_layout_to_grid()

    if args.ruler:
        diagram.add_ruler()

    diagram.save_to_file(args.diagram_file)
    diagram.remove_objects()
    if args.sqft:
        print(diagram.square_footage())

    if not args.wall_file:
        return

    wall_table = WallTable(wall_file=args.wall_file, clear=args.wall_clear)
    wall_table.update_wall_file(diagram)

    if args.recreate_diagram:
        wall_table.recreate_diagram_file(args.recreate_diagram)


def parse_args(cli_args):
    parser = ArgumentParser(description='The layout_model will'
                                        ' create/update a diagram and wall file'
                                        ' as inputs to the generate_svg')
    parser.add_argument('--input-file', '-i', default=None,
                        help='path to the input diagram file')
    parser.add_argument('--diagram-file', '-d', default=None,
                        help='path to the output the diagram-file which'
                             ' defaults to the input file')
    parser.add_argument('--wall-file', '-w', default=None,
                        help='path to the wall-file which is a seaborn_table'
                             ' file defining the wall, door, and window'
                             ' height. Defaults to the same as the '
                             ' --input-file with the markdown extension.')
    parser.add_argument('--wall-clear', action='store_true', default=False,
                         help='recreate wall file from scratch')

    parser.add_argument('--width', type=int, default=None,
                        help='number of feet per row in the file.  If specified'
                             ' then it will change the width in the diagram'
                             ' file, else it will default to the width of the'
                             ' diagram file or 400')
    parser.add_argument('--height', type=int, default=None,
                        help='number of feet of rows in the file.  If specified'
                             ' then it will change the width in the diagram'
                             ' file, else it will default to the width of the'
                             ' diagram file or 400')

    # HELPFUL FLAGS
    parser.add_argument('--checker', action='store_true', default=False,
                        help='checkers the background to see the 1 foot and 10'
                             ' foot squares')
    parser.add_argument('--ruler', '-r',
                        action='store_true', default=False,
                        help='puts a header of a ruler values in the file')
    parser.add_argument('--sqft', action='store_true', default=False,
                        help='prints a list of all rooms (with names) and their'
                             'square footage')

    # DEBUG ARGUMENTS which should not be used without --diagram-file specified.
    parser.add_argument('--highlight-room', default=None, nargs='+',
                        help='highlights a room with this name to test room'
                             ' dimensions for debugging')
    parser.add_argument('--remove-objects', default=None, action='store_true',
                        help='remove objects and boundaries for debugging')
    parser.add_argument('--remove-names', default=None, action='store_true',
                        help='remove names from rooms')
    parser.add_argument('--recreate-diagram', default=None,
                        help='path to a diagram file which if specified will'
                             ' be generated based on the wall file, for debug'
                             ' purposes.  This file will not have the objects'
                             ' or virtual walls so it should not be used to '
                             ' override the original --diagram-file')

    parser.add_argument('--backup-folder', '-b', default='./_backup',
                        help='path to the input file which will be cleaned'
                             ' name of the rooms')

    args = parser.parse_args(cli_args)
    if args.diagram_file is None and any(
            [args.remove_names, args.remove_objects]):
        print("--remove-names and --remove-objects should"
              " not be used without specifying a different diagram file")
        sys.exit(1)
    if args.input_file and args.diagram_file is None:
        args.diagram_file = args.input_file
    if args.input_file is None:
        args.wall_file = None
    if args.input_file is None:
        if args.diagram_file is None:
            print('One of the following options must be specified, --input-file'
                  ' or --diagram-file are ')
            sys.exit(1)
        if args.height is None:
            args.height = 400
        if args.width is None:
            args.width = 200

    if args.wall_file is None:
        args.wall_file = f'{args.diagram_file.rsplit(".", 1)[0]}.md'

    if (args.wall_file and args.wall_file != '-' and
            args.wall_file == os.path.basename(args.wall_file)):
        args.wall_file = os.path.join(os.path.dirname(args.diagram_file),
                                      args.wall_file)
    if (args.diagram_file != '-' and
            args.diagram_file == os.path.basename(args.diagram_file)):
        args.diagram_file = os.path.join(os.path.dirname(args.input_file),
                                         args.diagram_file)

    return args


def backup_files(files, backup_folder):
    if backup_folder and not os.path.exists(backup_folder):
        os.mkdir(backup_folder)
    for file in files:
        if backup_folder and file and os.path.exists(file):
            copyfile(file, os.path.join(backup_folder, os.path.basename(file)))


if __name__ == '__main__':
    main()