"""Rule-based event generator for tracking data, supporting config-based rules."""


class EventDetector:
    def __init__(self, loitering_threshold_sec: float = 10.0,
                 stopped_threshold_sec: float = 5.0,
                 wrong_direction_rules: dict = None,
                 config: dict = None):
        """
        loitering_threshold_sec: duration a person must be in view (or in a zone) to trigger loitering
        stopped_threshold_sec: duration an object must be stationary to trigger stopped
        wrong_direction_rules: dict mapping zone name to expected direction
        config: dict containing full pipeline config
        """
        self.config = config or {}
        evt_cfg = self.config.get("events", {})

        self.loitering_threshold_sec = evt_cfg.get("suspicious_loitering_threshold_sec", loitering_threshold_sec)
        self.stopped_threshold_sec = stopped_threshold_sec
        self.wrong_direction_rules = wrong_direction_rules or {
            "Main Road": "north"
        }

        # Configurable thresholds
        self.running_speed_threshold = evt_cfg.get("running_speed_threshold", 8.0)
        self.crowd_threshold_size = evt_cfg.get("crowd_threshold_size", 4)
        self.long_stop_threshold_sec = evt_cfg.get("long_stop_threshold_sec", 20.0)
        self.suspicious_loitering_threshold_sec = evt_cfg.get("suspicious_loitering_threshold_sec", 15.0)
        self.prolonged_parking_threshold_sec = evt_cfg.get("prolonged_parking_threshold_sec", 30.0)

    def detect(self, class_name: str, duration_sec: float, motion_meta: dict, spatial_meta: dict, relationships: dict = None) -> list:
        """Evaluate rules to generate a list of triggered event strings for a track.

        Returns:
            list of strings (e.g. ["entered", "loitering", "exited", "running", ...])
        """
        events = []

        # 1. Entry / Appeared
        events.append("entered")

        # 2. Exit / Disappeared (since we analyze completed tracks offline, they have exited)
        events.append("exited")

        # 3. Stopped
        if motion_meta.get("speed") == "stationary" and duration_sec >= self.stopped_threshold_sec:
            events.append("stopped")

        # 4. Loitering (legacy simple rule)
        if class_name == "person":
            is_slow_or_stopped = motion_meta.get("speed") in ("stationary", "slow")
            if duration_sec >= self.loitering_threshold_sec and is_slow_or_stopped:
                events.append("loitering")

        # 5. Zone entrance / Gate crossing
        entered_z = spatial_meta.get("entered_zone")
        if entered_z and entered_z != "outside":
            zone_event_name = f"entered_{entered_z.lower().replace(' ', '_')}"
            events.append(zone_event_name)

        # 6. Wrong direction vehicle in lane
        if class_name in ("car", "motorcycle", "bus", "truck"):
            curr_zone = spatial_meta.get("current_zone")
            vehicle_dir = motion_meta.get("direction", "unknown")
            
            if curr_zone in self.wrong_direction_rules:
                expected_dir = self.wrong_direction_rules[curr_zone]
                if vehicle_dir not in ("unknown", "stationary"):
                    is_opposite = False
                    if expected_dir == "north" and "south" in vehicle_dir:
                        is_opposite = True
                    elif expected_dir == "south" and "north" in vehicle_dir:
                        is_opposite = True
                    elif expected_dir == "east" and "west" in vehicle_dir:
                        is_opposite = True
                    elif expected_dir == "west" and "east" in vehicle_dir:
                        is_opposite = True
                    
                    if is_opposite:
                        events.append("wrong_direction")

        # 7. Running (person moving fast)
        if class_name == "person" and motion_meta.get("speed") == "fast":
            events.append("running")

        # 8. Crowd Detection
        if class_name == "person" and relationships:
            g_size = relationships.get("group_size", 1)
            if g_size >= self.crowd_threshold_size:
                events.append("crowd")

        # 9. Long Stop
        stat_dur = motion_meta.get("stationary_duration", 0.0)
        if stat_dur >= self.long_stop_threshold_sec:
            events.append("long_stop")

        # 10. Suspicious Loitering (person loitering in sensitive zones: Gate/Parking)
        curr_z = spatial_meta.get("current_zone", "outside")
        dwell_z = spatial_meta.get("total_dwell_time", 0.0)
        if class_name == "person" and curr_z in ("Entrance Gate", "Parking Area") and dwell_z >= self.suspicious_loitering_threshold_sec:
            events.append("suspicious_loitering")

        # 11. Prolonged Vehicle Parking (vehicle stopped in Parking Area or Entrance Gate)
        if (class_name in ("car", "motorcycle", "bus", "truck") and 
                curr_z in ("Entrance Gate", "Parking Area") and 
                stat_dur >= self.prolonged_parking_threshold_sec):
            events.append("prolonged_vehicle_parking")

        # Clean duplicate events (keeping order)
        unique_events = []
        for e in events:
            if e not in unique_events:
                unique_events.append(e)

        return unique_events
