import pytest
import structures

class TestSubrange:
    def testGettingSingleValue(self):
        array = range(20)

        range1 = structures.Subrange(array, 5, 5)

        assert range1[0] == 5
        assert range1[1] == 6

    def testGettingSlice(self):
        array = list(range(20))

        range1 = structures.Subrange(array, 5, 5)

        assert range1[2:5] == [7, 8, 9]

    def testSettingSingleValue(self):
        array = list(range(20))

        range1 = structures.Subrange(array, 3, 7)
        range1[4] = 42

        assert array[7] == 42

    def testSettingSliceValue(self):
        array = list(range(20))

        range1 = structures.Subrange(array, 4, 10)
        range1[3:7] = [42, 42, 42, 42]

        assert array == [0, 1, 2, 3, 4, 5, 6, 42, 42, 42, 42, 11, 12, 13, 14, 15, 16, 17, 18, 19]
