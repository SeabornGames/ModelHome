'''This module uses the seaborn_model_house.boxes to render a single room'''
from seaborn_model_house.boxes import Boxes, edges, svgutil


class ModelHouseBox(Boxes):
    def __init__(self, output_file, *args):
        super().__init__()
        self.addSettingsArgs(edges.FingerJointSettings)
        self.parseArgs(args)
        self.output = output_file
        svgutil.SVGFile.METADATA = 'Created by RenderBox'
        self.open()

    def render_room_floor(self, room):
        pass # todo

    def render_room_wall(self, wall_row):
        pass # todo
