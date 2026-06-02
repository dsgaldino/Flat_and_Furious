"""Shared constants for cycling activity types."""

CYCLING_STRAVA_TYPES = ("Ride", "VirtualRide")
CYCLING_ACTIVITY_TYPES = frozenset(CYCLING_STRAVA_TYPES)


def filter_cycling(df):
    """Keep Ride and VirtualRide rows from a formatted activities DataFrame."""
    if "activity_type" not in df.columns:
        return df[df["distance"].notna()].copy()
    return df[df["activity_type"].isin(CYCLING_ACTIVITY_TYPES)].copy()
