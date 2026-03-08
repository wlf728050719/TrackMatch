import argparse
import os
from pathlib import Path

import geopandas as gpd
import pandas as pd
from gotrackit.map.Net import Net
from gotrackit.MapMatch import MapMatch
from shapely.geometry import Point

from utils.load_shp import load_link, load_node


def save_result(truth_nodes_gdf, extend_nodes_gdf, match_res, link_gdf, root_dir, sub_dir, track_id):
    if root_dir is not None:
        output_dir = Path(root_dir) / str(sub_dir) / str(track_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        # 导出实际轨迹点shp
        truth_nodes_shp_path = output_dir / 'truth_nodes.shp'
        truth_nodes_gdf.to_file(truth_nodes_shp_path, encoding='utf-8')

        # 导出记录轨迹点shp
        extend_nodes_shp_path = output_dir / 'extend_nodes.shp'
        extend_nodes_gdf.to_file(extend_nodes_shp_path, encoding='utf-8')

        # 导出预测csv文件
        match_res.to_csv(os.path.join(output_dir, 'match_res.csv'), encoding='utf_8_sig', index=False)

        # 导出预测shp文件
        try:
            node_df = match_res.copy()
            node_df['geometry'] = [Point(xy) for xy in zip(node_df['prj_lng'], node_df['prj_lat'])]
            node_gdf_out = gpd.GeoDataFrame(node_df, geometry='geometry', crs='EPSG:4326')
            node_shp_path = output_dir / 'predict_node.shp'
            node_gdf_out.to_file(node_shp_path, encoding='utf-8', driver='ESRI Shapefile')

            match_res['link_id'] = match_res['link_id'].astype(link_gdf['link_id'].dtype)
            merged_links = pd.merge(match_res, link_gdf[['link_id', 'geometry']], on='link_id', how='left')
            valid_links = merged_links.dropna(subset=['geometry'])
            link_gdf_out = gpd.GeoDataFrame(valid_links, geometry='geometry', crs=link_gdf.crs)
            link_shp_path = output_dir / 'predict_link.shp'
            link_gdf_out.to_file(link_shp_path, encoding='utf-8', driver='ESRI Shapefile')

        except Exception as e:
            print(f"  -> Error generating visualization files: {e}")


def change_format(data):
    gdf = pd.DataFrame(data)
    gdf['time'] = pd.to_datetime(gdf['time'])
    gdf['time'] = gdf['time'].astype('int64') // 10 ** 9
    gdf['geometry'] = [Point(xy) for xy in zip(gdf['lng'], gdf['lat'])]
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry', crs='EPSG:4326')
    return gdf


def match_static_track(link_gdf, node_gdf, truth_nodes_data, all_record_nodes, min_record_nodes, max_miss_nodes,
                       allowed_links, track_id="test", root_dir=None):
    # net初始化
    my_net = Net(link_gdf=link_gdf, node_gdf=node_gdf, cut_off=1200.0)
    my_net.init_net()

    # 获取真实经过节点gdf
    truth_nodes_gdf = change_format(truth_nodes_data)

    # 保留记录点以及其前后一点记录
    all_record_node_set = set(all_record_nodes)
    all_node_ids = truth_nodes_data['node_id'].tolist()

    record_indices = [i for i, nid in enumerate(all_node_ids) if nid in all_record_node_set]
    keep_indices = set()
    for idx in record_indices:
        keep_indices.add(idx)
        if idx > 0:
            keep_indices.add(idx - 1)
        if idx < len(all_node_ids) - 1:
            keep_indices.add(idx + 1)
    keep_indices = sorted(keep_indices)
    extend_nodes_data = truth_nodes_data.iloc[keep_indices].copy()
    # 非直接记录点heading置为0
    extend_nodes_data['heading'] = extend_nodes_data.apply(
        lambda row: row['heading'] if row['node_id'] in all_record_node_set else 0.0,
        axis=1
    )

    # 获取扩充后节点gdf
    extend_nodes_gdf = change_format(extend_nodes_data)
    truth_record_nodes = set(extend_nodes_data['node_id'].tolist()) & set(all_record_nodes)

    # 轨迹匹配
    mpm = MapMatch(net=my_net, flag_name='xa_sample',  # 指定项目名称xa_sample
                   use_sub_net=True,  # 启用子网络
                   gps_buffer=100, top_k=20,  # GPS点空间关联半径取100米，选取GPS点100米范围内最近的20个路段作为候选路段
                   dense_gps=False,  # 不增密GPS点
                   use_heading_inf=True, omitted_l=6.0,  # 启用GPS航向角矫正，若前后点GPS距离<=6米，将忽略航向角的修正
                   del_dwell=True, dwell_l_length=50.0, dwell_n=0,  # 停留点删除参数
                   export_html=False, export_geo_res=False, use_gps_source=False,  # 输出设置参数
                   gps_radius=15.0, export_all_agents=False,  # 输出设置参数
                   )
    match_res, warn_info, error_info = mpm.execute(gps_df=extend_nodes_gdf)

    if warn_info or error_info:
        # 模型预测警告或错误
        save_result(truth_nodes_gdf, extend_nodes_gdf, match_res, link_gdf, root_dir, 2, track_id)
        return 2

    if len(truth_record_nodes) < min_record_nodes:
        # 路径经过记录点少于最小记录数
        save_result(truth_nodes_gdf, extend_nodes_gdf, match_res, link_gdf, root_dir, 3, track_id)
        return 3
    # 节点判断
    predict_record_nodes = set(pd.concat([match_res['from_node'], match_res['to_node']]).unique()) & set(
        all_record_nodes)
    if len(predict_record_nodes) < len(truth_record_nodes):
        # 模型预测轨迹记录点小于实际记录数(如果模型预测正确,不应该在不经过的节点被记录，即模型预测错误)
        save_result(truth_nodes_gdf, extend_nodes_gdf, match_res, link_gdf, root_dir, 4, track_id)
        return 4
    else:
        missing_nodes = predict_record_nodes - truth_record_nodes
        diff_count = len(missing_nodes)
        # 模型预测轨迹记录点大于实际记录点
        if diff_count <= max_miss_nodes:
            # 记录点识别遗漏小于阈值
            all_predicted_links = match_res['link_id'].dropna()
            # 去除预测偏差较大的首尾部分路径
            if len(all_predicted_links) > 2:
                middle_links = all_predicted_links.iloc[1:-1]
            else:
                middle_links = all_predicted_links

            middle_link_set = set(x for x in middle_links.unique())
            if middle_link_set.issubset(allowed_links):
                # 预测路径均为规定路径
                save_result(truth_nodes_gdf, extend_nodes_gdf, match_res, link_gdf, root_dir, 1, track_id)
                return 1
            else:
                # 预测路径存在违规路径
                save_result(truth_nodes_gdf, extend_nodes_gdf, match_res, link_gdf, root_dir, 0, track_id)
                return 0
        else:
            # 记录点识别遗漏大于阈值
            save_result(truth_nodes_gdf, extend_nodes_gdf, match_res, link_gdf, root_dir, 5, track_id)
            return 5


def main():
    parser = argparse.ArgumentParser(description='静态轨迹匹配')
    parser.add_argument('-link_file', type=str, required=True, help='link文件路径')
    parser.add_argument('-node_file', type=str, required=True, help='node文件路径')
    parser.add_argument('-link_pmd', type=str, default='None', help='link处理方法')
    parser.add_argument('-node_pmd', type=str, default='None', help='node处理方法')
    parser.add_argument('-track_id', type=int, help='轨迹ID')
    parser.add_argument('-track_file', type=str, required=True, help='track文件路径')
    parser.add_argument('-available_link_file', required=True, type=str, help='允许路径')
    parser.add_argument('-record_nodes', type=int, nargs='+', required=True,
                        metavar='ID', help='记录节点ID列表')
    parser.add_argument('-min_record_nodes', type=int, default=3, help='最少记录节点')
    parser.add_argument('-max_miss_nodes', type=int, default=1, help='最大错过节点')
    parser.add_argument('-root_dir', type=str, help='输出根目录')
    args = parser.parse_args()

    link_gdf = load_link(args.link_file, args.link_pmd)
    node_gdf = load_node(args.node_file, args.node_pmd)

    with open(args.available_link_file, 'r', encoding='utf-8') as f:
        allowed_links = set(int(line.strip()) for line in f if line.strip())

    truth_nodes_data = pd.read_json(args.track_file)
    print(
        match_static_track(link_gdf, node_gdf, truth_nodes_data, args.record_nodes, args.min_record_nodes,
                           args.max_miss_nodes, allowed_links, args.track_id, args.root_dir))


if __name__ == '__main__':
    main()
