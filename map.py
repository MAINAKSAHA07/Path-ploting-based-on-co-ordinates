import os
import pandas as pd
import folium
from folium import plugins
from datetime import datetime
import numpy as np
from geopy.distance import geodesic

# Folder where your CSV files are stored
input_folder = "data"  # Updated to relative path
output_map_path = "combined_map.html"  # Updated to relative path

# Initialize empty lists to collect all data
all_data = []

# Loop through all CSV files
for file_name in os.listdir(input_folder):
    if file_name.endswith(".csv"):
        file_path = os.path.join(input_folder, file_name)
        
        # Read the CSV
        df = pd.read_csv(file_path)
        
        # Check if required columns exist
        if all(col in df.columns for col in ['Latitude', 'Longitude', 'Heart Rate', 'Timestamp']):
            print(f"Adding data from {file_name}...")
            
            # Convert timestamp to datetime
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            
            # Sort by timestamp to ensure correct path
            df = df.sort_values('Timestamp')
            
            # Calculate distance between consecutive points
            df['Prev_Latitude'] = df['Latitude'].shift()
            df['Prev_Longitude'] = df['Longitude'].shift()
            
            # Apply geodesic distance
            df['Distance_meters'] = df.apply(
                lambda row: geodesic((row['Prev_Latitude'], row['Prev_Longitude']),
                                   (row['Latitude'], row['Longitude'])).meters
                if pd.notnull(row['Prev_Latitude']) else 0, axis=1)
            
            # Calculate speed in m/s
            df['Time_diff'] = df['Timestamp'].diff().dt.total_seconds()
            df['Speed_mps'] = df['Distance_meters'] / df['Time_diff']
            
            # Extend the data list
            all_data.extend(df[['Latitude', 'Longitude', 'Heart Rate', 'Timestamp', 'Distance_meters', 'Speed_mps']].values.tolist())
        else:
            print(f"Skipped {file_name} (missing required columns)")

# Convert to DataFrame for easier handling
data_df = pd.DataFrame(all_data, columns=['Latitude', 'Longitude', 'Heart Rate', 'Timestamp', 'Distance_meters', 'Speed_mps'])

# Check if we have collected any data
if len(data_df) == 0:
    print("❌ No data found. Please check your files!")
else:
    # Center the map at the mean coordinates
    center_lat = data_df['Latitude'].mean()
    center_lon = data_df['Longitude'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=15)
    
    # Create the path with heart rate color gradient
    coordinates = data_df[['Latitude', 'Longitude']].values.tolist()
    heart_rates = data_df['Heart Rate'].values.tolist()
    speeds = data_df['Speed_mps'].values.tolist()
    
    # Create color gradient based on heart rate
    min_hr = min(heart_rates)
    max_hr = max(heart_rates)
    
    # Normalize heart rates to 0-1 range for heatmap
    normalized_hr = [(hr - min_hr) / (max_hr - min_hr) for hr in heart_rates]
    
    # Add the path with color gradient
    for i in range(len(coordinates)-1):
        # Create color gradient (red intensity based on heart rate)
        color = f'#{int(255 * normalized_hr[i]):02x}0000'
        
        # Draw path segment
        folium.PolyLine(
            locations=[coordinates[i], coordinates[i+1]],
            color=color,
            weight=4,
            opacity=0.8
        ).add_to(m)
        
        # Add markers for suspicious movements (speed > 10 m/s or ~36 km/h)
        if speeds[i] > 10:
            folium.CircleMarker(
                location=coordinates[i],
                radius=5,
                color='red',
                fill=True,
                popup=f'Suspicious Movement<br>Speed: {speeds[i]:.1f} m/s<br>Heart Rate: {heart_rates[i]} BPM'
            ).add_to(m)
    
    # Prepare heatmap data
    heatmap_data = []
    for i in range(len(coordinates)):
        lat, lon = coordinates[i]
        weight = normalized_hr[i]  # Use normalized heart rate as weight
        heatmap_data.append([lat, lon, weight])
    
    # Add heatmap layer
    plugins.HeatMap(
        heatmap_data,
        radius=15,
        blur=10,
        max_zoom=1,
        min_opacity=0.3,
    ).add_to(m)
    
    # Add start and end markers
    folium.Marker(
        coordinates[0],
        popup=f'Start<br>Heart Rate: {heart_rates[0]} BPM<br>Time: {data_df["Timestamp"].iloc[0]}',
        icon=folium.Icon(color='green', icon='info-sign')
    ).add_to(m)
    
    folium.Marker(
        coordinates[-1],
        popup=f'End<br>Heart Rate: {heart_rates[-1]} BPM<br>Time: {data_df["Timestamp"].iloc[-1]}',
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    
    # Add a legend for the path colors
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 200px; height: 150px; 
                border:2px solid grey; z-index:9999; background-color:white;
                opacity:0.8;
                font-size:12px;
                padding: 10px">
                <strong>Legend</strong><br>
                Path Color:<br>
                &nbsp; <i style="background: #ff0000; display: inline-block; width: 15px; height: 15px;"></i>&nbsp; High Heart Rate<br>
                &nbsp; <i style="background: #800000; display: inline-block; width: 15px; height: 15px;"></i>&nbsp; Medium Heart Rate<br>
                &nbsp; <i style="background: #400000; display: inline-block; width: 15px; height: 15px;"></i>&nbsp; Low Heart Rate<br>
                <br>
                Markers:<br>
                &nbsp; <i class="fa fa-info-circle" style="color:green"></i>&nbsp; Start Point<br>
                &nbsp; <i class="fa fa-info-circle" style="color:red"></i>&nbsp; End Point<br>
                &nbsp; <i class="fa fa-circle" style="color:red"></i>&nbsp; Suspicious Movement<br>
                <br>
                Heatmap shows heart rate intensity
                </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the combined map
    m.save(output_map_path)
    print(f"✅ Combined map saved at: {output_map_path}")
    print(f"Heart Rate Range: {min_hr:.0f} - {max_hr:.0f} BPM")
    
    # Print suspicious movements summary
    suspicious_movements = data_df[data_df['Speed_mps'] > 10]
    if len(suspicious_movements) > 0:
        print("\nSuspicious Movements Detected:")
        print(f"Total suspicious points: {len(suspicious_movements)}")
        print(f"Maximum speed: {suspicious_movements['Speed_mps'].max():.1f} m/s")
        print(f"Average speed during suspicious movements: {suspicious_movements['Speed_mps'].mean():.1f} m/s")
    else:
        print("\nNo suspicious movements detected (all speeds < 10 m/s)")
