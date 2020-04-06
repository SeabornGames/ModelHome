import os
import sys
from argparse import ArgumentParser

from seaborn_model_house.diagram import Diagram
from seaborn_model_house.wall_table import WallTable
from seaborn_model_house.model_house_box import ModelHouseBox


def main(cli_args=sys.argv[1:]):
    args = parse_args(cli_args)

    diagram = Diagram(args.diagram_file) if args.diagram_file else None
    wall_table = WallTable(wall_file=args.wall_file) if args.wall_file else None
    if wall_table:
        if args.update_wall_file:
            wall_table.update_wall_file(diagram)
            wall_table.save()
        wall_table.assign_default(args)

    box = ModelHouseBox(args.output_file) if args.output_file else None
    rooms = get_rooms_to_render(args, diagram, wall_table)
    for room in rooms:
        if args.output_file is None:
            if box is not None:
                box.close()
            box = ModelHouseBox(
                os.path.join(args.output_folder, f'{room.lower()}.svg'))
        if diagram:
            box.render_room_floor(diagram.get_room(room), args.scale)

        if wall_table is not None:
            for row in wall_table:
                if (row['room_0'] == room or
                        (args.second_room_wall and row['room_1'] == room)):
                    box.render_room_wall(row, args.scale)
    box.close()


def get_rooms_to_render(args, diagram, wall_table):
    rooms = args.filter_rooms
    if rooms is None and diagram is not None:
        rooms = diagram.rooms
    if rooms is None and wall_table is not None:
        rooms = [row['room_0'] for row in wall_table]
        rooms+= [row['room_1'] for row in wall_table if row['room_1']]
    rooms = list(set(rooms))
    for exclude in (args.exclude_rooms or []):
        if exclude in rooms:
            rooms.remove(exclude)
    return rooms


def parse_args(cli_args):
    parser = ArgumentParser(description='The generate_svg will render a diagram'
                                        ' and/or wall_file into svg files.')
    parser.add_argument('--diagram-file', '-d', default=None,
                        help='path to the input diagram-file.  If not'
                             ' specified then the floors will not be created.')
    parser.add_argument('--wall-file', '-w', default=None,
                        help='path to the wall-file which is a seaborn_table'
                             ' file defining the wall, door, and window'
                             ' height.  If not specified then the walls will'
                             ' not be created.')
    parser.add_argument('--update-wall-file', default=False,
                        action='store_true',
                        help='If this flag is specified then a wall file'
                             ' named after --diagram-file will be created and'
                             ' used.')
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
    parser.add_argument('--output-file', default=None,
                        help='if specified then this will override the'
                             ' --output-folder and put all the rooms in a'
                             ' single file')
    parser.add_argument('--scale', default=24.0, type=float,
                        help='The number of mm in the output to equal a foot'
                             ' in the model')
    parser.add_argument('--filter-rooms', default=None, nargs='+',
                        help='Only generate walls and floors for these rooms.')
    parser.add_argument('--exclude-rooms', default=None, nargs='+',
                        help='Exclude these rooms from generating walls and'
                             ' floors.')
    parser.add_argument('--second-room-wall', default=False,
                        action='store_true',
                        help='if specified then walls will be rendered in '
                             ' secondary rooms as well.')
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

    if args.update_wall_file and args.wall_file is None:
        args.wall_file = f"{args.diagram_file.rsplit('.', 1)[0]}.md"

    if (args.wall_file and args.wall_file != '-' and
            args.wall_file == os.path.basename(args.wall_file)):
        args.wall_file = os.path.join(os.path.dirname(args.diagram_file),
                                      args.wall_file)

    if not os.path.exists(args.output_folder):
        os.mkdir(args.output_folder)
    return args


if __name__ == '__main__':
    main()