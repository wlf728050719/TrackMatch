import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from tqdm import tqdm

from generate.static_track_json import generate_static_track
from match.static_track_json import match_static_track
from utils.load_shp import load_link, load_node


def eval(od_paths, node_gdf, link_gdf, allowed_links, all_record_nodes, min_record_nodes, max_miss_nodes,
         skip_path_tuples=None, debug=False, output_dir=None):
    true_labels = []
    predict_labels = []

    allowed_links_set = set(allowed_links)
    all_record_nodes_set = set(all_record_nodes)
    skip_path_tuples = skip_path_tuples or set()

    for idx, path_info in tqdm(enumerate(od_paths), total=len(od_paths), desc="Evaluating OD paths"):
        nodes = path_info["nodes"]
        links = path_info["links"]

        if tuple(nodes) in skip_path_tuples:
            continue

        true_label = 1 if set(links).issubset(allowed_links_set) else 0
        true_labels.append(true_label)

        if debug and output_dir:
            track_data = generate_static_track(node_gdf, nodes, f"{output_dir}/od_{idx}.json")
        else:
            track_data = generate_static_track(node_gdf, nodes)
        truth_nodes_df = pd.DataFrame(track_data)

        prd_label = match_static_track(
            link_gdf=link_gdf,
            node_gdf=node_gdf,
            truth_nodes_data=truth_nodes_df,
            all_record_nodes=all_record_nodes_set,
            min_record_nodes=min_record_nodes,
            max_miss_nodes=max_miss_nodes,
            allowed_links=allowed_links_set,
            track_id=f"od_path_{idx}",
            root_dir=None
        )
        predict_labels.append(prd_label)

        if debug:
            print(f"[OD {idx}] true: {true_label}, prd: {prd_label}")

    return true_labels, predict_labels


def eval_all(od_paths_dir, node_file, node_pmd, link_file, link_pmd,
             min_record_nodes, max_miss_nodes, all_record_nodes_file, available_link_file,
             output_dir, extra_allowed_path_file=None, debug=False):
    link_gdf = load_link(link_file, link_pmd)
    node_gdf = load_node(node_file, node_pmd)

    with open(available_link_file, 'r', encoding='utf-8') as f:
        allowed_links = set(int(line.strip()) for line in f if line.strip())
    with open(all_record_nodes_file, 'r', encoding='utf-8') as f:
        all_record_nodes = [int(line.strip()) for line in f if line.strip()]

    extra_allowed_path_nodes = []
    if extra_allowed_path_file:
        with open(extra_allowed_path_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    nodes = [int(x) for x in line.split()]
                    extra_allowed_path_nodes.append(nodes)
        extra_path_tuples = {tuple(p) for p in extra_allowed_path_nodes}
    else:
        extra_path_tuples = set()
        extra_allowed_path_nodes = []

    all_true_labels = []
    all_predict_labels = []

    od_paths_dir = Path(od_paths_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sub_dirs = [d for d in od_paths_dir.iterdir() if d.is_dir()]

    for subdir in sub_dirs:
        result_json = subdir / "result.json"
        with open(result_json, 'r', encoding='utf-8') as f:
            result = json.load(f)
        od_paths = result.get("paths", [])
        true_labels, predict_labels = eval(
            od_paths=od_paths,
            node_gdf=node_gdf,
            link_gdf=link_gdf,
            allowed_links=allowed_links,
            all_record_nodes=all_record_nodes,
            min_record_nodes=min_record_nodes,
            max_miss_nodes=max_miss_nodes,
            skip_path_tuples=extra_path_tuples,
            debug=debug,
            output_dir=output_dir
        )
        all_true_labels.extend(true_labels)
        all_predict_labels.extend(predict_labels)

    if extra_allowed_path_nodes:
        print(f"Evaluating {len(extra_allowed_path_nodes)} extra paths (global)...")
        allowed_links_set = set(allowed_links)
        all_record_nodes_set = set(all_record_nodes)

        for e_idx, nodes in tqdm(enumerate(extra_allowed_path_nodes), total=len(extra_allowed_path_nodes),
                                 desc="Evaluating extra paths"):
            true_labels.append(1)  # 强制为合法

            if debug and output_dir:
                track_data = generate_static_track(node_gdf, nodes, f"{output_dir}/extra_{e_idx}.json")
            else:
                track_data = generate_static_track(node_gdf, nodes)
            truth_nodes_df = pd.DataFrame(track_data)

            prd_label = match_static_track(
                link_gdf=link_gdf,
                node_gdf=node_gdf,
                truth_nodes_data=truth_nodes_df,
                all_record_nodes=all_record_nodes_set,
                min_record_nodes=min_record_nodes,
                max_miss_nodes=max_miss_nodes,
                allowed_links=allowed_links_set,
                track_id=f"extra_path_{e_idx}",
                root_dir=None
            )
            all_true_labels.append(1)
            all_predict_labels.append(prd_label)

            if debug:
                print(f"[Extra {e_idx}] true: 1, prd: {prd_label}")

    # 转为 numpy array
    y_true = np.array(all_true_labels)
    y_prd = np.array(all_predict_labels)

    # 绘制混淆矩阵
    cm = confusion_matrix(y_true, y_prd)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(cmap=plt.cm.Blues)
    plt.title("Confusion Matrix")
    plt.savefig(output_dir / "confusion_matrix.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 保存配置
    config = {
        "min_record_nodes": min_record_nodes,
        "max_miss_nodes": max_miss_nodes,
        "all_record_nodes_file": str(all_record_nodes_file),
        "available_link_file": str(available_link_file),
        "extra_allowed_path_file": str(extra_allowed_path_file) if extra_allowed_path_file else None,
        "total_samples": len(y_true),
        "num_extra_paths": len(extra_allowed_path_nodes)
    }
    with open(output_dir / "config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    return y_true, y_prd

def main():
    parser = argparse.ArgumentParser(description='生成动态轨迹')
    parser.add_argument('-link_file', type=str, required=True, help='link文件路径')
    parser.add_argument('-node_file', type=str, required=True, help='node文件路径')
    parser.add_argument('-link_pmd', type=str, default='None', help='link处理方法')
    parser.add_argument('-node_pmd', type=str, default='None', help='node处理方法')
    parser.add_argument('-od_paths_dir', type=str, required=True, help='od路径文件根目录')
    parser.add_argument('-available_link_file', required=True, type=str, help='允许路径')
    parser.add_argument('-all_record_nodes_file', type=str, required=True, help='所有记录文件路径')
    parser.add_argument('-extra_allowed_path_file', type=str, required=False, help='额外的合规路径文件')
    parser.add_argument('-min_record_nodes', type=int, default=3, help='最少记录节点')
    parser.add_argument('-max_miss_nodes', type=int, default=1, help='最大错过节点')
    parser.add_argument('-output_dir', type=str, help='输出根目录')
    parser.add_argument('-debug', action='store_true', help='debug')
    args = parser.parse_args()
    eval_all(args.od_paths_dir, args.node_file, args.node_pmd, args.link_file, args.link_pmd, args.min_record_nodes,
             args.max_miss_nodes, args.all_record_nodes_file, args.available_link_file, args.output_dir,
             args.extra_allowed_path_file, args.debug)


if __name__ == '__main__':
    main()
