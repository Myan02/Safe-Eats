import os
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self, raw_path, processed_path):
        self.raw_path = raw_path
        self.processed_path = processed_path
        Path(processed_path).parent.mkdir(parents=True, exist_ok=True)

    def needs_cleaning(self):
        if not os.path.exists(self.processed_path):
            return True
        if not os.path.exists(self.raw_path):
            return False
        return os.path.getmtime(self.raw_path) > os.path.getmtime(self.processed_path)

    def clean_data(self):
        if not self.needs_cleaning():
            logger.info("Loading existing cleaned data")
            return pd.read_csv(self.processed_path)

        logger.info("Starting data cleaning")
        try:
            df = self._load_and_standardize()
            df = self._handle_missing_data(df)
            df = self._remove_duplicates(df)
            self._save_clean_data(df)
            return df
        except Exception as e:
            logger.error(f"Cleaning failed: {str(e)}")
            raise

    def _load_and_standardize(self):
        df = pd.read_csv(self.raw_path, dtype={
            'dba': str,
            'building': str,
            'street': str,
            'boro': str,
            'zipcode': str,
            'latitude': str,
            'longitude': str
        })
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.replace('[^a-z0-9]', '_', regex=True)
        
        # Ensure required columns
        required = ['dba', 'building', 'street', 'boro', 'zipcode', 'latitude', 'longitude']
        for col in required:
            if col not in df.columns:
                df[col] = np.nan
                logger.warning(f"Missing column: {col}")
        
        return df[required]

    def _handle_missing_data(self, df):
        """Strict coordinate validation"""
        # Convert to numeric, forcing invalid to NaN
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        
        # Remove rows with any invalid coordinates
        initial_count = len(df)
        df = df.dropna(subset=['latitude', 'longitude'], how='any')
        
        # Validate coordinate ranges
        valid_lat = df['latitude'].between(-90, 90)
        valid_lon = df['longitude'].between(-180, 180)
        df = df[valid_lat & valid_lon]
        
        logger.info(f"Removed {initial_count - len(df)} rows with invalid coordinates")
        return df.reset_index(drop=True)

    def _remove_duplicates(self, df):
        """Safe deduplication"""
        df = df.sort_values(by=['latitude', 'longitude'], na_position='last')
        df = df.drop_duplicates(
            subset=['dba', 'building', 'street', 'boro'],
            keep='first'
        )
        return df

    def _save_clean_data(self, df):
        df.to_csv(self.processed_path, index=False)
        logger.info(f"Saved cleaned data: {len(df)} records")