import json
import math
import os
from typing import Optional

class LocationService:
    def __init__(self):
        path = os.path.join("data", "calming_spots.json")
        with open(path, "r") as f:
            data = json.load(f)
        self.spots = data["spots"]

    NEEDS_SPOT_KEYWORDS = [
        "calm down", "find a place", "somewhere quiet",
        "need to sit", "panic", "anxiety", "overwhelmed",
        "breathing", "can't handle", "too much"
    ]

    def needs_calming_spot(self, message: str) -> bool:
        msg = message.lower()
        return any(k in msg for k in self.NEEDS_SPOT_KEYWORDS)

    def _haversine(self, lat1, lng1, lat2, lng2):
        R = 6371000  # meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lng2 - lng1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
        return 2 * R * math.asin(math.sqrt(a))

    def find_nearest_calming_spot(self, user_location: dict) -> Optional[dict]:
        if not user_location or "lat" not in user_location:
            return None
        lat, lng = user_location["lat"], user_location["lng"]

        nearest = None
        best_dist = float("inf")
        for spot in self.spots:
            d = self._haversine(lat, lng, spot["lat"], spot["lng"])
            if d < best_dist:
                best_dist = d
                nearest = spot

        if nearest:
            nearest["distance_m"] = int(best_dist)
        return nearest

    def all_spots(self):
        return self.spots
