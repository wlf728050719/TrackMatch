import argparse
import geopandas as gpd
import os


def main():
    parser = argparse.ArgumentParser(description='shp文件转csv')
    parser.add_argument('-input_file', type=str, help='shp文件路径')
    parser.add_argument('-output_file', type=str, help='csv文件路径')
    args = parser.parse_args()
    output_dir = os.path.dirname(args.output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    gpd.read_file(args.input_file).to_csv(args.output_file, index=False)
    print('Export Finished')


if __name__ == '__main__':
    main()
