import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

class WaitTimePredictor:
    def __init__(self):
        self.model = LinearRegression()
        self._train_dummy_model()
        
    def _train_dummy_model(self):
        # Training dataset simulating historical clinic logs:
        # Features: [queue_position, priority_score, doctor_active_load]
        # Target: wait_time_minutes
        X_train = np.array([
            [1, 1, 2],
            [2, 3, 5],
            [5, 2, 8],
            [1, 5, 1],
            [3, 2, 4],
            [4, 1, 6]
        ])
        y_train = np.array([5, 18, 45, 8, 25, 35]) # Wait time in minutes
        
        self.model.fit(X_train, y_train)
        
    def predict_wait_time(self, queue_position, priority_score, doctor_active_load):
        features = np.array([[queue_position, priority_score, doctor_active_load]])
        predicted_time = self.model.predict(features)[0]
        return max(2, int(round(predicted_time)))

# Singleton instance for app import
wait_time_model = WaitTimePredictor()