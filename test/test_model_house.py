import unittest
from test.support import BaseTest


class ModelHouseTest(BaseTest):

    def test_installation(self):
        from model_house.boxes import Boxes, edges
        expected_file = self.test_data_path('expected', f'{self.name}.svg')
        result_file = self.test_data_path('result', f'{self.name}.svg')
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