# qrl_service.py
#!/usr/bin/env python3
"""
QRL + Traffic Forecasting Service Layer

This module combines:
- FGCUTrafficForecaster (classical ML)
- QRLTrafficAgent (quantum policy)

Into a single function that returns a JSON-like dict
with both forecast and risk classification.
"""

import datetime
from typing import Dict

from .traffic_forecasting import FGCUTrafficForecaster
from .qrl_traffic_agent import QRLTrafficAgent

# Initialize once at import time
_forecaster = FGCUTrafficForecaster()
# Try to load existing models first; if not found, train on synthetic data
if not _forecaster.load_models():
    _forecaster.train_models()

_qrl_agent = QRLTrafficAgent()


def get_segment_status(segment_id: str, hours_ahead: int = 1) -> Dict:
    """
    Core function to get both:
    - traffic forecast for a segment
    - QRL-based risk classification for that forecast

    This is what your API layer should call and return as JSON.
    """
    # Use existing forecaster to predict traffic
    preds = _forecaster.predict_traffic(segment_id, hours_ahead=hours_ahead)

    if not preds:
        return {
            "error": "No predictions available",
            "segment_id": segment_id,
        }

    # For now, just use the first prediction in the horizon
    first = preds[0]
    ts = datetime.datetime.fromisoformat(first["timestamp"])
    volume = first["predicted_volume"]
    hour = ts.hour

    # QRL risk classification
    qrl_output = _qrl_agent.classify_risk(volume=volume, hour=hour)

    return {
        "segment_id": segment_id,
        "timestamp": first["timestamp"],
        "forecast": {
            "predicted_volume": volume,
            "confidence": first["confidence"],
            "rf_prediction": first["rf_prediction"],
            "gb_prediction": first["gb_prediction"],
        },
        "qrl_risk": qrl_output,
    }


if __name__ == "__main__":
    # Local smoke test
    result = get_segment_status("fgcu_blvd", hours_ahead=3)
    import json
    print(json.dumps(result, indent=2))
