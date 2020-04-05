import logging
import os
import sys
import unittest

from seaborn_model_house import layout_model, generate_svg, ModelHouseBox

PATH = os.path.split(os.path.abspath(__file__))[0]
log = logging.getLogger(__file__)
logging.basicConfig(level=os.getenv('TEST_LOG_LEVEL', 'INFO'),
                    format="%(message)s",
                    handlers=[logging.StreamHandler(sys.__stdout__)])


class BaseTest(unittest.TestCase):
    maxDiff = None

    def assert_result_file(self, expected_file, result_file, message=None):
        with open(expected_file, 'rb') as fp:
            expected = fp.read().decode('utf-8').replace('\r', '').split('\n')

        with open(result_file, 'rb') as fp:
            result = fp.read().decode('utf-8').replace('\r', '').split('\n')

        for i in range(len(result)):
            # todo remove this when the surface problem is fixed
            expected[i] = expected[i].split('id="surface')[0]
            result[i] = result[i].split('id="surface')[0]
            self.assertEqual(expected[i], result[i], message)

    @staticmethod
    def get_test_data_path(*args):
        path = os.path.join(PATH, 'data', *args)
        if not os.path.exists(os.path.dirname(path)):
            os.mkdir(os.path.dirname(path))
        return path

    @staticmethod
    def remove_file(file):
        os.remove(file)
        if not os.listdir(os.path.dirname(file)):
            os.rmdir(os.path.dirname(file))

    @property
    def name(self):
        return self.id().split('.')[-1]

    def expected_file(self, ext='svg'):
        return self.get_test_data_path('expected', f'{self.name}.{ext}')

    def result_file(self, ext='svg'):
        return self.get_test_data_path('result', f'{self.name}.{ext}')


class BoxesTest(BaseTest):
    def test_installation(self):
        box = ModelHouseBox(self.result_file())
        x = y = h = 100.0

        d2 = d3 = None
        box.rectangularWall(x, h, "FFFF", bedBolts=[d2] * 4, move="right")
        box.rectangularWall(y, h, "FfFf", bedBolts=[d3, d2, d3, d2], move="up")
        box.rectangularWall(y, h, "FfFf", bedBolts=[d3, d2, d3, d2])
        box.rectangularWall(x, h, "FFFF", bedBolts=[d2] * 4, move="left up")
        box.rectangularWall(x, y, "ffff", bedBolts=[d2, d3, d2, d3],
                            move="right")
        box.rectangularWall(x, y, "ffff", bedBolts=[d2, d3, d2, d3])
        box.close()
        self.assert_result_file(self.expected_file(), self.result_file())

    def test_uneven_height_box(self):
        box = ModelHouseBox(self.result_file())
        x = y = 100.0
        heights = [50.0, 50.0, 100.0, 100.0]
        box.bottom_edge = 'F'
        box.lid = True
        box.outside = False

        if box.outside:
            x = box.adjustSize(x)
            y = box.adjustSize(y)
            for i in range(4):
                heights[i] = box.adjustSize(
                    heights[i], box.bottom_edge, box.lid)

        h0, h1, h2, h3 = heights
        b = box.bottom_edge

        box.trapezoidWall(x, h0, h1, [b, "F", "e", "F"], move="right")
        box.trapezoidWall(y, h1, h2, [b, "f", "e", "f"], move="right")
        box.trapezoidWall(x, h2, h3, [b, "F", "e", "F"], move="right")
        box.trapezoidWall(y, h3, h0, [b, "f", "e", "f"], move="right")

        maxh = None
        with box.saved_context():
            if b != "e":
                box.rectangularWall(x, y, "ffff", move="up")

            if box.lid:
                maxh = max(heights)
                lidheights = [maxh - h for h in heights]
                h0, h1, h2, h3 = lidheights
                lidheights += lidheights
                edges = ["E" if (
                    lidheights[i] == 0.0 and lidheights[i + 1] == 0.0
                ) else "f" for i in range(4)]
                box.rectangularWall(x, y, edges, move="up")

        if box.lid:
            box.moveTo(0, maxh + box.edges["F"].spacing() +
                       box.edges[b].spacing() + 3 * box.spacing, 180)
            box.trapezoidWall(y, h0, h3, "Ffef",
                              move="right" if h0 and h3 else "right only")
            box.trapezoidWall(x, h3, h2, "FFeF",
                              move="right" if h3 and h2 else "right only")
            box.trapezoidWall(y, h2, h1, "Ffef",
                              move="right" if h2 and h1 else "right only")
            box.trapezoidWall(x, h1, h0, "FFeF",
                              move="right" if h1 and h0 else "right only")
        box.close()
        self.assert_result_file(self.expected_file(), self.result_file())


class LayoutModelTest(BaseTest):
    def test_create_empty_diagram_file(self):
        layout_model.main([
            '--diagram-file', self.result_file('txt'),
            '--width', '100',
            '--height', '100',
            '--checker', '--ruler',
            '--backup-folder', '',
        ])
        self.assert_result_file(self.expected_file('txt'),
                                self.result_file('txt'))

    def test_clean_diagram_file(self):
        layout_model.main([
            '--diagram-file', self.result_file('txt'),
            '--input-file', self.get_test_data_path('unclean_diagram.txt'),
            '--backup-folder', '',
        ])
        self.assert_result_file(self.expected_file('txt'),
                                self.result_file('txt'))

    def test_create_wall_file(self):
        if os.path.exists(self.result_file('md')):
            os.remove(self.result_file('md'))
        layout_model.main([
            '--input-file', self.get_test_data_path('unclean_diagram.txt'),
            '--diagram-file', self.result_file('txt'),
            '--backup-folder', '',
        ])
        layout_model.main([
            '--input-file', self.get_test_data_path('unclean_diagram.txt'),
            '--diagram-file', self.result_file('txt'),
            '--backup-folder', '',
        ])
        self.assert_result_file(self.expected_file('md'),
                                self.result_file('md'))

    def test_remove_objects(self):
        layout_model.main([
            '--input-file', self.get_test_data_path('unclean_diagram.txt'),
            '--diagram-file', self.result_file('txt'),
            '--backup-folder', '',
            '--remove-object',
        ])
        self.assert_result_file(self.expected_file('txt'),
                                self.result_file('txt'))

    def test_remove_virtual(self):
        layout_model.main([
            '--input-file', self.get_test_data_path('unclean_diagram.txt'),
            '--diagram-file', self.result_file('txt'),
            '--backup-folder', '',
            '--remove-object', '--remove-virtual'
        ])
        self.assert_result_file(self.expected_file('txt'),
                                self.result_file('txt'))


class GenerateSvgTest(BaseTest):
    def test_create_svg_file_with_diagram_only(self):
        generate_svg.main([
            '--diagram-file', self.get_test_data_path('unclean_diagram.txt'),
            '--output-file', self.result_file(),
        ])
        self.assert_result_file(self.expected_file(), self.result_file())

    def test_create_svg_file_with_wall_file_only(self):
        generate_svg.main([
            '--wall-file', self.get_test_data_path('wall_file.md'),
            '--output-file', self.result_file(),
        ])
        self.assert_result_file(self.expected_file(), self.result_file())

    def test_create_svg_file_with_wall_and_diagram(self):
        generate_svg.main([
            '--diagram-file', self.get_test_data_path('unclean_diagram.txt'),
            '--wall-file', self.get_test_data_path('wall_file.md'),
            '--output-file', self.result_file(),
        ])
        self.assert_result_file(self.expected_file(), self.result_file())


if __name__ == '__main__':
    unittest.main()
