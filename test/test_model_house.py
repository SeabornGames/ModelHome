import logging
import os
import sys
import unittest

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
            self.assertEqual(expected[i], result[i], message)

    def get_test_data_path(self, *args):
        path = os.path.join(PATH, 'data', *args)
        if not os.path.exists(os.path.dirname(path)):
            os.mkdir(os.path.dirname(path))
        return path

    def remove_file(self, file):
        os.remove(file)
        if not os.listdir(os.path.dirname(file)):
            os.rmdir(os.path.dirname(file))

    @property
    def name(self):
        return self.id().split('.')[-1]


class ModelHouseTest(BaseTest):
    def test_installation(self):
        from seaborn_model_house.boxes import Boxes, edges

        expected_file = self.get_test_data_path('expected', f'{self.name}.svg')
        result_file = self.get_test_data_path('result', f'{self.name}.svg')
        box = Boxes()
        box.addSettingsArgs(edges.FingerJointSettings)
        box.parseArgs(args=[
            '--output', result_file,
        ])
        box.open()
        d2 = edges.Bolts(2)
        box.rectangularWall(10, 10, "FFFF",
                            bedBolts=[d2] * 4,
                            move="right")
        box.close()
        self.assert_result_file(expected_file, result_file)


if __name__ == '__main__':
    unittest.main()
