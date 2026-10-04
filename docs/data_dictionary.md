# Data dictionary

**Forecast**: source_id, source_type, source_version, initialization_time,
valid_time, lead_time, lead_bucket, latitude, longitude, cell_id, region,
variable, forecast_value, unit, ensemble_member, regime, metadata

**Observation**: observation_time, latitude, longitude, cell_id, region,
variable, observed_value, unit, quality_flag, source

**Skill**: source_id, variable, region, lead_time, regime, window, mae,
rmse, bias, correlation, precision, recall, f1, sample_count, version, timestamp

**Weight**: case_id, source_id, assigned_weight, gate_type, model_version, timestamp

**Confidence**: case_id, forecast, confidence, lower_50/80/95, upper_50/80/95,
interval_width_80, disagreement_score, calibration_version, data_mode

**Risk**: case_id, hazard, probability, threshold, forecast, event_detected,
high_uncertainty, time_horizon_h, risk_priority_score, risk_category, data_mode
