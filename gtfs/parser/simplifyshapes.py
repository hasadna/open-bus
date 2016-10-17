"""
a script to simplify shapes.

The script uses an iterative implementation of Ramer-Douglas-Peucker line-simplification algorithm provided
by https://www.namekdev.net/2014/06/iterative-version-of-ramer-douglas-peucker-line-simplification-algorithm/

additional reference:
    http://en.wikipedia.org/wiki/Ramer-Douglas-Peucker_algorithm
    https://github.com/fhirschmann/rdp/issues/5
"""

from argparse import ArgumentParser
import csv
from .gtfs_reader import GTFS
import math
import numpy as np


def ramer_douglas_peucker_bit_array(points, epsilon):
    stk = [(0, len(points) - 1)]
    global_start_index = 0
    bit_array = np.ones(len(points), dtype=bool)

    while len(stk) > 0:
        start_index = stk[-1][0]
        last_index = stk[-1][1]
        stk.pop()

        dmax = 0.
        index = start_index

        for i in range(index + 1, last_index):
            if bit_array[i - global_start_index]:
                d = point_line_distance(points[i], points[start_index], points[last_index])
                if d > dmax:
                    index = i
                    dmax = d
        if dmax > epsilon:
            stk.append((start_index, index))
            stk.append((index, last_index))
        else:
            for i in range(start_index + 1, last_index):
                bit_array[i - global_start_index] = False
    return bit_array


def ramer_douglas_peucker(points, epsilon):
    bit_array = ramer_douglas_peucker_bit_array(points, epsilon)
    res_list = []
    for i in range(len(points)):
        if bit_array[i]:
            res_list.append(points[i])
    return res_list


def point_line_distance(point, start, end):
    if start == end :
        return math.sqrt((point[0] - start[0])**2 + (point[1] - start[1])**2)  # calculate distance between two points
    else:
        n = abs((end[0] - start[0]) * (start[1] - point[1]) - (start[0] - point[0]) * (end[1] - start[1]))
        d = math.sqrt((end[0] - start[0]) * (end[0] - start[0]) + (end[1] - start[1]) * (end[1] - start[1]))
        return n/d


def export_shapes(output_file_name, shapes):
    # shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence
    with open(output_file_name, 'w', encoding='utf8') as f:
        writer = csv.DictWriter(f, lineterminator='\n',
                                fieldnames='shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence'.split(','))
        writer.writeheader()
        for shape_id, coordinates in shapes.items():
            for shape_pt_sequence, coordinate in enumerate(coordinates):
                writer.writerow({'shape_id': shape_id,
                                 'shape_pt_lat': coordinate[0],
                                 'shape_pt_lon': coordinate[1],
                                 'shape_pt_sequence': shape_pt_sequence + 1})


def parse_flags():
    parser = ArgumentParser()
    parser.add_argument('--gtfs_file_name', default='gtfs/sample/israel-public-transportation.zip')
    parser.add_argument('--output_file_name', default='gtfs/sample/simplified_shapes.txt')
    parser.add_argument('--epsilon', default=0.0001)
    return parser.parse_args()


def main():
    args = parse_flags()
    g = GTFS(args.gtfs_file_name)
    g.load_shapes()
    simplified = {shape.shape_id: ramer_douglas_peucker(list(shape.coordinates.values()), args.epsilon) for shape in g.shapes.values()}
    export_shapes(args.output_file_name, simplified)

if __name__ == '__main__':
    main()
