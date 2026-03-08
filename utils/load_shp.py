import geopandas as gpd

def load_link(link_file, method="None"):
    link_gdf = gpd.read_file(link_file)
    if method == "None":
        return link_gdf
    else:
        raise NotImplementedError("Unknown Method")

def load_node(node_file, method="None"):
    node_gdf = gpd.read_file(node_file)
    if method == "None":
        return node_gdf
    else:
        raise NotImplementedError("Unknown Method")
