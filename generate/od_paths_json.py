import argparse
import os

import networkx as nx
import json
from utils.load_shp import load_link


def path_is_valid(path, max_repeat, start_node, end_node):
    node_counts = {node: path.count(node) for node in set(path)}
    return all(
        count <= max_repeat for node, count in node_counts.items() if node != start_node and node != end_node)


def generate_od_paths(link_file, link_pmd, start_node, end_node, root_dir, max_nodes, max_repeat, save_shp=False):
    # 构建图
    link_gdf = load_link(link_file, link_pmd)
    G = nx.MultiGraph()
    for idx, row in link_gdf.iterrows():
        G.add_edge(row['from_node'], row['to_node'], key=row['link_id'], length=row['length'], geometry=row['geometry'])
        G.add_edge(row['to_node'], row['from_node'], key=row['link_id'], length=row['length'], geometry=row['geometry'])

    # 查找简单路径
    print("Searching Paths...")
    all_simple_paths = nx.all_simple_paths(G, source=start_node, target=end_node, cutoff=max_nodes)
    valid_paths = [path for path in all_simple_paths if path_is_valid(path, max_repeat, start_node, end_node)]

    final_paths = []
    for path in valid_paths:
        links = []
        nodes = path
        for i in range(len(nodes) - 1):
            links.append(list(G[nodes[i]][nodes[i + 1]].keys())[0])
        final_paths.append({"nodes": nodes, "links": links})

    result = {"count": len(final_paths), "start_node": start_node, "end_node": end_node, "max_nodes": max_nodes,
              "max_repeat": max_repeat, "paths": final_paths}

    # 创建输出目录
    output_dir = os.path.join(root_dir, f"{start_node}_{end_node}")
    os.makedirs(output_dir, exist_ok=True)

    # 保存 result.json
    json_path = os.path.join(output_dir, "result.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    if save_shp:
        # 为每条路径生成对应的 .shp 文件
        for idx, path_info in enumerate(final_paths, start=0):
            print("Writing Shp File for path #{}".format(idx))
            link_ids = path_info["links"]
            path_gdf = link_gdf[link_gdf['link_id'].isin(link_ids)].copy()
            shp_path = os.path.join(output_dir, f"{idx}.shp")
            path_gdf.to_file(shp_path, encoding='utf-8')

    print("Generate Finished")


def main():
    parser = argparse.ArgumentParser("生成指定od路径")
    parser.add_argument('-link_file', type=str, required=True, help='link文件路径')
    parser.add_argument('-link_pmd', type=str, default='None', help='link处理方法')
    parser.add_argument('-start_node', type=int, required=True, help='开始node')
    parser.add_argument('-end_node', type=int, required=True, help='结束node')
    parser.add_argument('-root_dir', type=str, required=True, help='输出根目录')
    parser.add_argument('-max_nodes', type=int, required=True, help='最大节点数')
    parser.add_argument('-max_repeat', type=int, required=True, help='节点最大重复数')
    parser.add_argument('-save_shp', action='store_true', help='<UNK>')
    args = parser.parse_args()
    generate_od_paths(args.link_file, args.link_pmd, args.start_node, args.end_node, args.root_dir, args.max_nodes,
                      args.max_repeat,args.save_shp)


if __name__ == '__main__':
    main()
