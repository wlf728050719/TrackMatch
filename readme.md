shp文件转csv
```
python utils/export_csv.py -input_file data/map/中心线.shp -output_file export/中心线.csv
```

生成动态轨迹(车辆携带gps)
```
python generate_dynamic_track.py -link_file data/JuYe/中心线.shp -link_pmd JuYe -node_file data/JuYe/交叉点.shp -node_pmd JuYe -output_fldr track/dynamic/1  -start_node 1 -end_node 2 
```

匹配动态轨迹
```
python match_dynamic_track.py -link_file data/JuYe/中心线.shp -link_pmd JuYe -node_file data/JuYe/交叉点.shp -node_pmd JuYe -track_file track/dynamic/1/test-gps.shp -output_fldr match/dynamic/1
```

生成静态轨迹(固定拍摄点gps)
```
python generate_static_track.py -node_file data/JuYe/交叉点.shp -node_pmd JuYe -output_file track/static/1.json -node_list 1 2 3 4 5 6
```

匹配静态轨迹
```
python match_static_track.py -link_file data/JuYe/中心线.shp -link_pmd JuYe -node_file data/JuYe/交叉点.shp -node_pmd JuYe -track_file track/static/1.json -output_fldr match/static/1
```