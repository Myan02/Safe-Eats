"""Custom JSON encoder for Flask responses."""
from flask.json.provider import JSONProvider
import json
import pandas as pd
import numpy as np

class SafeEncoder(JSONProvider):
    """Handles pandas/numpy types in JSON serialization."""
    
    def dumps(self, obj, **kwargs):
        """Serialize objects with custom type handling."""
        def default_encoder(obj):
            if pd.isna(obj) or obj is None:
                return None
            if isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            if isinstance(obj, (pd.Timestamp, np.datetime64)):
                return obj.strftime('%Y-%m-%d')
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        return json.dumps(obj, default=default_encoder, **kwargs)

    def loads(self, s, **kwargs):
        """Default JSON deserialization."""
        return json.loads(s, **kwargs)