'''This module uses the seaborn_model_house.boxes to render a single room'''
from seaborn_model_house.boxes import Boxes, edges, svgutil


class ModelHouseBox(Boxes):
    def __init__(self, output_file, *args):
        super().__init__()
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(edges.DuckbillSettings)
        self.parseArgs(args)
        self.output = output_file
        svgutil.SVGFile.METADATA = 'Created by RenderBox'
        self.open()

    def render_room_floor(self, room, scale):
        pass # todo

    def render_room_wall(self, wall_row, scale=24):
        return # todo
        mm_scale = scale / 4
        if wall_row['horizontal']:
            left_edge='f'
            right_edge='F'
        else:
            left_edge='F'
            right_edge='f'
        bottom_edge='f'
        top_edge='E'

        self.trapezoidWall(
            w=len(wall_row['symbols']) * mm_scale,
            h0=wall_row['height_1'] * mm_scale,
            h1=wall_row['height_2'] * mm_scale,
            edges = [bottom_edge, left_edge, top_edge, right_edge],
            move='up')