import argparse
import json
import math
from datetime import datetime, timedelta

from utils.load_shp import load_node


def calculate_heading(lon1, lat1, lon2, lat2):
    dx = lon2 - lon1
    dy = lat2 - lat1
    angle_rad = math.atan2(dy, dx)
    # 转换为角度
    angle_deg = math.degrees(angle_rad)
    # 标准化到 [0, 360)
    if angle_deg < 0:
        angle_deg += 360.0

    return round(angle_deg, 2)


def generate_static_track(node_gdf, node_list, output_file):
    node_map = {}
    for idx, row in node_gdf.iterrows():
        nid = int(row['node_id']) if not isinstance(row['node_id'], int) else row['node_id']
        geom = row['geometry']
        node_map[nid] = {
            'lng': geom.x,
            'lat': geom.y
        }
    # 验证 node_list 中的节点是否都在数据中
    for nid in node_list:
        if nid not in node_map:
            raise ValueError(f"Node ID {nid} not found in the input data.")
    # 初始化时间和代理ID
    current_time = datetime.now()
    agent_id = "test"
    trajectory_data = []

    # 预计算所有路段的航向
    segment_headings = []
    for i in range(len(node_list) - 1):
        start_id = node_list[i]
        end_id = node_list[i + 1]

        p1 = node_map[start_id]
        p2 = node_map[end_id]

        h = calculate_heading(p1['lng'], p1['lat'], p2['lng'], p2['lat'])
        segment_headings.append(h)

    # 生成轨迹点
    for i, nid in enumerate(node_list):
        coords = node_map[nid]
        # 计算时间：起始时间 + i * 5分钟
        point_time = current_time + timedelta(minutes=5 * i)
        time_str = point_time.strftime('%Y-%m-%d %H:%M:%S.%f')
        if i < len(segment_headings):
            current_heading = segment_headings[i]
        else:

            current_heading = segment_headings[-1]
        point = {
            "time": time_str,
            "heading": current_heading,
            "agent_id": agent_id,
            "lng": coords['lng'],
            "lat": coords['lat']
        }
        trajectory_data.append(point)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(trajectory_data, f, indent=4, ensure_ascii=False)
    print(f"Generate Finished: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='生成动态轨迹')
    parser.add_argument('-node_file', type=str, help='node文件路径')
    parser.add_argument('-node_pmd', type=str, default='None', help='node处理方法')
    parser.add_argument('-output_file', type=str, help='输出文件')
    parser.add_argument('-node_list', type=int, nargs='+', required=True,
                        metavar='ID', help='节点ID列表')
    args = parser.parse_args()

    node_gdf = load_node(args.node_file, args.node_pmd)
    generate_static_track(node_gdf,args.node_list,args.output_file)
