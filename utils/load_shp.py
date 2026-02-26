import geopandas as gpd

def load_link(link_file, method="None"):
    link_gdf = gpd.read_file(link_file)
    if method == "None":
        return link_gdf
    elif method == "JuYe":
        # 移除speed,Id,添加road_name
        link_gdf = link_gdf.drop(columns=['speed'])
        link_gdf = link_gdf.drop(columns=['Id'])
        link_gdf['road_name'] = 'unknown'
        return link_gdf
    else:
        raise NotImplementedError("Unknown Method")

def load_node(node_file, method="None"):
    node_gdf = gpd.read_file(node_file)
    if method == "None":
        return node_gdf
    elif method == "JuYe":
        # 移除Id 重命名mode_id
        node_gdf = node_gdf.rename(columns={'mode_id': 'node_id'})
        node_gdf = node_gdf.drop(columns=['Id'])
        return node_gdf
    else:
        raise NotImplementedError("Unknown Method")
