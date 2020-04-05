'''This module uses the seaborn_model_house.boxes to render a single room'''
from seaborn_model_house.boxes import Boxes, edges, svgutil


class RenderBox(Boxes):
    def __init__(self, output_file, *args, doc=''):
        super().__init__()
        self.addSettingsArgs(edges.FingerJointSettings)
        self.parseArgs(args)
        self.output = output_file
        if doc:
            svgutil.SVGFile.METADATA = doc
        self.open()

    def render_room_floor(self, room):
        pass # todo

    def render_room_wall(self, wall_row):
        pass # todo
