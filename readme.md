# Path Plotting Based on Coordinates

## Overview

This project visualizes GPS data by plotting paths based on latitude and longitude coordinates from CSV files. It also analyzes heart rate data, calculates distances between points, and identifies suspicious movements based on speed.

## Features

- **Path Visualization**: Displays the route taken with color gradients based on heart rate.
- **Heatmap**: Shows the intensity of heart rates along the path.
- **Suspicious Movement Detection**: Identifies and marks points where the speed exceeds a specified threshold (e.g., 10 m/s).
- **Distance Calculation**: Computes the distance between consecutive GPS points using geodesic calculations.
- **Speed Analysis**: Calculates speed based on the distance and time between points.

## Requirements

- Python 3.x
- Pandas
- Folium
- Geopy
- Numpy

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install pandas folium geopy numpy
   ```

## Usage

1. Place your CSV files containing latitude, longitude, heart rate, and timestamp data in the `data` folder.
2. Run the script:
   ```bash
   python map.py
   ```

3. Open the generated `combined_map.html` file in your web browser to view the visualization.

## Output

The output of the script is an interactive map saved as `combined_map.html`. Below is an example of what the map looks like:

![Map Visualization](path/to/your/screenshot.png)

### Example Map Features:
- **Path Color Legend**: Indicates heart rate levels along the path.
- **Markers**: 
  - Green marker for the start point
  - Red marker for the end point
  - Red circle markers for suspicious movements

## Data Format

The CSV files should contain the following columns:
- `Timestamp`: The time of the data point.
- `Latitude`: The latitude of the location.
- `Longitude`: The longitude of the location.
- `Heart Rate`: The heart rate at that time.

## Example CSV Structure

```csv
Timestamp,Heart Rate,Latitude,Longitude
2025-04-14 12:47:14,95,33.423717676018,-111.93959632563052
2025-04-14 12:47:15,95,33.423717676018,-111.93959632563052
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Folium](https://python-visualization.github.io/folium/) for mapping capabilities.
- [Geopy](https://geopy.readthedocs.io/en/stable/) for distance calculations.
- [Pandas](https://pandas.pydata.org/) for data manipulation.

## Contact

For any questions or feedback, please reach out to msaha4@asu.edu.