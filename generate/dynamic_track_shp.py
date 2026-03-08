import argparse
import os
from utils.load_shp import load_link, load_node
from gotrackit.map.Net import Net
from gotrackit.generation.SampleTrip import TripGeneration


def main():
    parser = argparse.ArgumentParser(description='生成动态轨迹')
    parser.add_argument('-link_file', type=str, required=True, help='link文件路径')
    parser.add_argument('-node_file', type=str, required=True, help='node文件路径')
    parser.add_argument('-link_pmd', type=str, default='None', help='link处理方法')
    parser.add_argument('-node_pmd', type=str, default='None', help='node处理方法')
    parser.add_argument('-start_node', type=int, required=True, help='开始node')
    parser.add_argument('-end_node', type=int, required=True, help='结束node')
    parser.add_argument('-output_fldr', type=str, required=True, help='输出目录')
    args = parser.parse_args()

    link_gdf = load_link(args.link_file, args.link_pmd)
    node_gdf = load_node(args.node_file, args.node_pmd)

    # 构建一个net, 要求路网线层和路网点层必须是WGS-84, EPSG:4326 地理坐标系
    my_net = Net(link_gdf=link_gdf, node_gdf=node_gdf, is_check=True)
    my_net.init_net()  # 路网对象初始化
    # 新建一个行程生成类
    ts = TripGeneration(net=my_net, loc_error_sigma=50.0, loc_frequency=30, time_step=0.1)
    od_set = [(args.start_node, args.end_node)]
    os.makedirs(args.output_fldr, exist_ok=True)
    ts.generate_od_trips(od_set=od_set, out_fldr=args.output_fldr, time_format="%Y-%m-%d %H:%M:%S.%f",
                         agent_flag='test', instant_output=False, file_type='shp',
                         start_year=2026)

if __name__ == '__main__':
    main()
