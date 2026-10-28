# ## Hurricane Tracking Workflow
# This notebook selects trackpoints from a features class of trackpoints for a selected storm (season & name), creates a track line, and extracts US counties that intersect that trackline. 
# 
# Fall 2026
# tallulah.bowden@duke.edu

#Import package
import arcpy
from pathlib import Path

#Set paths
project_folder = Path(__file__).parent
raw_folder_path = project_folder.parent / 'data' / 'raw'
processed_folder_path = project_folder.parent / 'data' / 'processed'

#Arcpy environment settings
arcpy.env.workspace = str(raw_folder_path)
arcpy.env.overwriteOutput = True

#Set storm variable
storm_season = 2000
affected_counties = processed_folder_path / 'affected_counties.shp'

#Set model layers
ibtracs_NA_points = str(raw_folder_path /'IBTrACS_NA.shp')
usa_counties = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Counties_Generalized_Boundaries/FeatureServer/0'
storm_track_points =  "memory\\track_points"
storm_track_line = "memory\\Tracklines"


storm_dict = {}

for storm_season in range(2000,2004):
    storm_names = []


    cursor = arcpy.da.SearchCursor(
        in_table = ibtracs_NA_points,
        field_names = ['NAME'],
        where_clause = f'SEASON = {storm_season}')

    # Iterate through cursor and print name
    for record in cursor:
        storm_name = record[0]
        if not storm_name in storm_names and storm_name != 'UNNAMED':
            storm_names.append(storm_name) 


    # Delete cursor
    del(cursor)

    storm_dict[storm_season] = storm_names


# #### Select point features corresponding to a specific storm (season & name)
# Iterate and tally storm county counts

for storm_season in storm_dict.keys():
    storm_count_total = 0
    for storm_name in storm_dict[storm_season]:
            
        #Select points for a given storm
        arcpy.analysis.Select(
            in_features=ibtracs_NA_points, 
            out_feature_class=storm_track_points, 
            where_clause=f"SEASON = {storm_season} And NAME = '{storm_name}'"
        )

        # #### Connect Points to a Track line

        #Connect point to a track line
        arcpy.management.PointsToLine(
            Input_Features=storm_track_points,
            Output_Feature_Class=storm_track_line,
            Sort_Field='ISO_TIME'
        )

        #### Select Counties Intersecting Point

        #Select intersecting counties
        select_output = arcpy.management.SelectLayerByLocation(
            in_layer=usa_counties, 
            overlap_type="INTERSECT", 
            select_features=storm_track_line, 
            )
        select_result = select_output.getOutput(0)

        county_count = int(arcpy.management.GetCount(select_result).getOutput(0))
        storm_count_total += county_count
    

# Print the count

# %%
