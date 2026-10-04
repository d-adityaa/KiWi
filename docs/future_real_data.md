# Future real-data integration

Seams exist so real providers can be added without redesigning the core:

- `ForecastSource.fetch(variable, valid_time, lead_time)` → Forecast schema
- `ObservationSource.fetch(variable, start, end)` → Observation schema

Planned adapters (NOT implemented): GFS, ECMWF open data, IMD WRF, GraphCast,
Pangu-Weather, IMD observations, ERA5, AWS/rain gauges, radar/satellite.

Other future items: operational retraining scheduling, district-level
bulletins, additional Indian languages, advanced probabilistic calibration,
gridded national deployment, downscaling, GNN nowcasting.
