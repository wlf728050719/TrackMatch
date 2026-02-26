import argparse
import os

import geopandas as gpd
import pandas as pd
from gotrackit.map.Net import Net
from gotrackit.MapMatch import MapMatch

from utils.load_shp import load_node, load_link

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='动态轨迹匹配')
    parser.add_argument('-link_file', type=str, help='link文件路径')
    parser.add_argument('-node_file', type=str, help='node文件路径')
    parser.add_argument('-track_file', type=str, help='track文件路径')
    parser.add_argument('-link_pmd', type=str, default='None', help='link处理方法')
    parser.add_argument('-node_pmd', type=str, default='None', help='node处理方法')
    parser.add_argument('-output_fldr', type=str, help='输出目录')
    args = parser.parse_args()

    link_gdf = load_link(args.link_file, args.link_pmd)
    node_gdf = load_node(args.node_file, args.node_pmd)

    my_net = Net(link_gdf=link_gdf, node_gdf=node_gdf, cut_off=1200.0)
    my_net.init_net()  # net初始化
    gps_df = gpd.read_file(args.track_file)
    gps_df['time'] = pd.to_datetime(gps_df['time'])
    gps_df['time'] = gps_df['time'].astype('int64') // 10 ** 9
    mpm = MapMatch(net=my_net, flag_name='xa_sample',  # 指定项目名称xa_sample
                   use_sub_net=True,  # 启用子网络
                   gps_buffer=100, top_k=20,  # GPS点空间关联半径取100米，选取GPS点100米范围内最近的20个路段作为候选路段
                   dense_gps=False,  # 不增密GPS点
                   use_heading_inf=True, omitted_l=6.0,  # 启用GPS航向角矫正，若前后点GPS距离<=6米，将忽略航向角的修正
                   del_dwell=True, dwell_l_length=50.0, dwell_n=0,  # 停留点删除参数
                   export_html=True, export_geo_res=True, use_gps_source=True,  # 输出设置参数
                   gps_radius=15.0, export_all_agents=False,  # 输出设置参数
                   out_fldr=args.output_fldr)  # 输出设置参数

    # execute函数返回三个结果:
    # 第一个是匹配结果表、第二个是警告信息、第三个是错误信息
    match_res, warn_info, error_info = mpm.execute(gps_df=gps_df)
    match_res.to_csv(os.path.join(args.output_fldr, 'match_res.csv'), encoding='utf_8_sig', index=False)
    print(warn_info)
    print(error_info)