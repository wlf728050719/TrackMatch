shp文件转csv
```
python utils/export_csv.py -input_file data/map/中心线.shp -output_file export/中心线.csv
```

生成动态轨迹shp(车辆携带gps)
```
python generate/dynamic_track_shp.py -link_file data/map/中心线.shp  -node_file data/map/交叉点.shp  -output_fldr data/generate_tracks/dynamic/1_2  -start_node 1 -end_node 2 
```

匹配动态轨迹shp
```
python match/dynamic_track_shp.py -link_file data/map/中心线.shp  -node_file data/map/交叉点.shp  -track_file data/generate_tracks/dynamic/1_2/test-gps.shp -output_fldr data/match_results/dynamic/1_2
```

生成静态轨迹json(固定拍摄点gps)
```
python generate/static_track_json.py -node_file data/map/交叉点.shp  -output_file data/generate_tracks/static/test/0.json -node_list 55 45 44 43 41 37 31 30 28 25
python generate/static_track_json.py -node_file data/map/交叉点.shp  -output_file data/generate_tracks/static/test/1.json -node_list 55 45 44 43 49 53 57 62 70 74 81 82 91 90 86 85 92 99 102 101 88 72 65 61 54 37 31 30 28 25
python generate/static_track_json.py -node_file data/map/交叉点.shp  -output_file data/generate_tracks/static/test/2.json -node_list 55 45 44 43 49 53 57 62 70 74 81 82 91 90 86 85 92 99 102 101 106 110 118
python generate/static_track_json.py -node_file data/map/交叉点.shp  -output_file data/generate_tracks/static/test/3.json -node_list 55 45 44 43 41 37 54 61 65 72 88 101 106 110 118
python generate/static_track_json.py -node_file data/map/交叉点.shp  -output_file data/generate_tracks/static/test/4.json -node_list 118 110 106 101 88 72 65 61 54 37 31 30 28 25
python generate/static_track_json.py -node_file data/map/交叉点.shp  -output_file data/generate_tracks/static/test/5.json -node_list 118 110 106 101 102 99 92 85 86 90 91 82 81 74 70 62 57 53 49 43 41 37 31 30 28 25
python generate/static_track_json.py -node_file data/map/交叉点.shp  -output_file data/generate_tracks/static/test/6.json -node_list 137 138 139 140 141 142 143 144 145 146 147 149 150 148
python generate/static_track_json.py -node_file data/map/交叉点.shp  -output_file data/generate_tracks/static/test/7.json -node_list 137 138 139 140 141 142 143 144 165 171 174 180 181 182 172 169 158 149 150 148

```

匹配静态轨迹json
55 43 37 25 102 101 137 144 149 180 148 118 90
55 45 34 43 13 16 91 85 102 120 118 101 54 37 47 25 137 144 149 148 180 181
```
python match/static_track_json.py -link_file data/map/中心线.shp  -node_file data/map/交叉点.shp -available_link_file data/map/available_link.txt -track_file data/generate_tracks/static/test/0.json -track_id 0 -record_nodes 55 43 37 25 102 101 137 144 149 180 148 118 90  -min_record_nodes 3  -max_miss_nodes 1 -root_dir data/match_results/static/test 
python match/static_track_json.py -link_file data/map/中心线.shp  -node_file data/map/交叉点.shp -available_link_file data/map/available_link.txt -track_file data/generate_tracks/static/test/1.json -track_id 1 -record_nodes 55 43 37 25 102 101 137 144 149 180 148 118 90 -min_record_nodes 3  -max_miss_nodes 1 -root_dir data/match_results/static/test 
python match/static_track_json.py -link_file data/map/中心线.shp  -node_file data/map/交叉点.shp -available_link_file data/map/available_link.txt -track_file data/generate_tracks/static/test/2.json -track_id 2 -record_nodes 55 43 37 25 102 101 137 144 149 180 148 118 90 -min_record_nodes 3  -max_miss_nodes 1 -root_dir data/match_results/static/test
python match/static_track_json.py -link_file data/map/中心线.shp  -node_file data/map/交叉点.shp -available_link_file data/map/available_link.txt -track_file data/generate_tracks/static/test/3.json -track_id 3 -record_nodes 55 43 37 25 102 101 137 144 149 180 148 118 90 -min_record_nodes 3  -max_miss_nodes 1 -root_dir data/match_results/static/test
python match/static_track_json.py -link_file data/map/中心线.shp  -node_file data/map/交叉点.shp -available_link_file data/map/available_link.txt -track_file data/generate_tracks/static/test/4.json -track_id 4 -record_nodes 55 43 37 25 102 101 137 144 149 180 148 118 90 -min_record_nodes 3  -max_miss_nodes 1 -root_dir data/match_results/static/test
python match/static_track_json.py -link_file data/map/中心线.shp  -node_file data/map/交叉点.shp -available_link_file data/map/available_link.txt -track_file data/generate_tracks/static/test/5.json -track_id 5 -record_nodes 55 43 37 25 102 101 137 144 149 180 148 118 90 -min_record_nodes 3  -max_miss_nodes 1 -root_dir data/match_results/static/test
python match/static_track_json.py -link_file data/map/中心线.shp  -node_file data/map/交叉点.shp -available_link_file data/map/available_link.txt -track_file data/generate_tracks/static/test/6.json -track_id 6 -record_nodes 55 43 37 25 102 101 137 144 149 180 148 118 90 -min_record_nodes 3  -max_miss_nodes 1 -root_dir data/match_results/static/test
python match/static_track_json.py -link_file data/map/中心线.shp  -node_file data/map/交叉点.shp -available_link_file data/map/available_link.txt -track_file data/generate_tracks/static/test/7.json -track_id 7 -record_nodes 55 43 37 25 102 101 137 144 149 180 148 118 90 -min_record_nodes 3  -max_miss_nodes 1 -root_dir data/match_results/static/test
```

生成od轨迹json
```
python generate/od_paths_json.py -link_file data/map/中心线.shp  -start_node 55  -end_node 25 -max_nodes 20 -max_repeat 1 -root_dir data/od_paths 
python generate/od_paths_json.py -link_file data/map/中心线.shp  -start_node 55  -end_node 118 -max_nodes 20 -max_repeat 1 -root_dir data/od_paths
python generate/od_paths_json.py -link_file data/map/中心线.shp  -start_node 118  -end_node 25 -max_nodes 20 -max_repeat 1 -root_dir data/od_paths  
python generate/od_paths_json.py -link_file data/map/中心线.shp  -start_node 137  -end_node 148 -max_nodes 20 -max_repeat 1 -root_dir data/od_paths 
```

评估记录节点
```
python eval/record_nodes.py -link_file data/map/中心线.shp -node_file data/map/交叉点.shp  -od_paths_dir data/od_paths -available_link_file data/map/available_link.txt -all_record_nodes_file data/eval_results/2/all_record_nodes.txt -min_record_nodes 3  -max_miss_nodes 1 -output_dir  data/eval_results/2 -extra_allowed_path_file data/eval_results/2 /extra_allowed_path.txt
```