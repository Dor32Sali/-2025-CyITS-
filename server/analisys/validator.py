# analysis/validator.py

from typing import Any, Dict, List, Optional

# Tunable thresholds
MAX_SPEED = 150
EDGE_SPIKE_RATIO = 3.0      # 3x more than previous
EDGE_SPIKE_ABS = 100        # +100 vehicles vs previous
ALL_RED_QUEUE_THRESHOLD = 20


def validate_snapshot(
    snapshot: Dict[str, Any],
    prev_snapshot: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Validate one intersection snapshot.
    Returns a list of anomaly/attack dicts (ready for frontend).
    """
    intersection_id = snapshot.get("intersection_id", "UNKNOWN")

    light_state = snapshot.get("light_state", {}) or {}
    sensors = snapshot.get("sensor_readings", {}) or {}

    cam = sensors.get("CAMERA_DATA", {}) or {}
    rcu = sensors.get("RCU_DATA", {}) or {}
    loop = sensors.get("LOOP_DATA", {}) or {}

    anomalies: List[Dict[str, Any]] = []

    def add(code: str, message: str, severity: str = "WARN", attack: bool = False) -> None:
        anomalies.append({
            "intersection_id": intersection_id,
            "code": code,
            "severity": severity,          # INFO / WARN / ERROR / CRITICAL
            "is_attack_suspected": attack, # True if we think it's an attack pattern
            "message": message,
        })

    # -------------------------------------------------
    # 1. Basic range checks
    # -------------------------------------------------

    hour = cam.get("Hour_of_Day")
    if hour is not None and not (0 <= hour <= 23):
        add("CAMERA_HOUR_OUT_OF_RANGE",
            f"Hour_of_Day={hour} (expected 0–23)")

    cam_speed = cam.get("Avg_Speed")
    if cam_speed is not None and not (0 <= cam_speed <= MAX_SPEED):
        add("CAMERA_SPEED_OUT_OF_RANGE",
            f"Avg_Speed={cam_speed} (expected 0–{MAX_SPEED})")

    loop_speed = loop.get("Loop_Avg_Speed")
    if loop_speed is not None and not (0 <= loop_speed <= MAX_SPEED):
        add("LOOP_SPEED_OUT_OF_RANGE",
            f"Loop_Avg_Speed={loop_speed} (expected 0–{MAX_SPEED})")

    for field in ["Direction_Imbalance", "Blocked_to_Served_Ratio"]:
        val = cam.get(field)
        if val is not None and not (0 <= val <= 1):
            add("CAMERA_RATIO_OUT_OF_RANGE",
                f"{field}={val} (expected 0–1)")

    for field in ["CSW_Warn_Rate", "SPAT_TX_Rate", "IM_Fwd_Drop_Rate"]:
        val = rcu.get(field)
        if val is not None and not (0 <= val <= 1):
            add("RCU_RATIO_OUT_OF_RANGE",
                f"{field}={val} (expected 0–1)")

    for field in ["Loop_Occupancy_Ratio", "Truck_Ratio"]:
        val = loop.get(field)
        if val is not None and not (0 <= val <= 1):
            add("LOOP_RATIO_OUT_OF_RANGE",
                f"{field}={val} (expected 0–1)")

    # Non-negative counts
    def non_negative(name: str, val: Any):
        if val is not None and val < 0:
            add("NEGATIVE_COUNT", f"{name}={val} (expected >= 0)")

    non_negative("North_Cars", cam.get("North_Cars"))
    non_negative("South_Cars", cam.get("South_Cars"))
    non_negative("East_Cars", cam.get("East_Cars"))
    non_negative("West_Cars", cam.get("West_Cars"))
    non_negative("Queue_Length", cam.get("Queue_Length"))
    non_negative("Blocked_Cars", cam.get("Blocked_Cars"))
    non_negative("Loop_Vehicle_Count", loop.get("Loop_Vehicle_Count"))

    # -------------------------------------------------
    # 2. Phase vs lights – PHASE_DESYNC
    # -------------------------------------------------

    phase = rcu.get("Phase")

    expected_lights = {}
    if phase == "NS_GREEN":
        expected_lights = {"N": "GREEN", "S": "GREEN", "E": "RED", "W": "RED"}
    elif phase == "EW_GREEN":
        expected_lights = {"N": "RED", "S": "RED", "E": "GREEN", "W": "GREEN"}
    elif phase == "ALL_RED":
        expected_lights = {"N": "RED", "S": "RED", "E": "RED", "W": "RED"}

    if expected_lights:
        mismatches = {}
        for d, expected_color in expected_lights.items():
            actual_color = light_state.get(d)
            if actual_color is not None and actual_color != expected_color:
                mismatches[d] = {"expected": expected_color, "actual": actual_color}

        if mismatches:
            add(
                "PHASE_DESYNC",
                f"Phase={phase} but lights mismatch: {mismatches}",
                severity="CRITICAL",
                attack=True,
            )

    # Extra case for NS_GREEN but N/S are RED
    if phase == "NS_GREEN":
        if light_state.get("N") == "RED" and light_state.get("S") == "RED":
            add(
                "PHASE_DESYNC_NS_GREEN_BUT_NS_RED",
                "Controller phase NS_GREEN but N/S lights are RED.",
                severity="CRITICAL",
                attack=True,
            )

    # -------------------------------------------------
    # 3. EDGE BLACKHOLE (attack vs failure)
    # -------------------------------------------------

    edge_ns = loop.get("Edge_Blackhole_NS")
    edge_ew = loop.get("Edge_Blackhole_EW")
    loop_count = loop.get("Loop_Vehicle_Count") or 0
    loop_occ = loop.get("Loop_Occupancy_Ratio") or 0.0

    total_cam_cars = sum(
        cam.get(k, 0) or 0
        for k in ("North_Cars", "South_Cars", "East_Cars", "West_Cars")
    )

    # If blackhole flag is on AND camera sees a lot of cars BUT loop sees almost nothing
    if edge_ns == 1 or edge_ew == 1:
        add(
            "EDGE_BLACKHOLE_FLAG",
            f"Edge blackhole flag set (NS={edge_ns}, EW={edge_ew}).",
            severity="WARN",
        )

        if total_cam_cars > 50 and loop_count < 5 and loop_occ < 0.02:
            add(
                "EDGE_BLACKHOLE_ATTACK",
                (
                    "Camera sees heavy traffic but loops see almost nothing "
                    f"(cam_total={total_cam_cars}, loop_count={loop_count}, "
                    f"loop_occ={loop_occ}). Possible edge blackhole attack."
                ),
                severity="CRITICAL",
                attack=True,
            )

    # -------------------------------------------------
    # 4. EDGE SPIKE SPOOF (requires prev_snapshot)
    # -------------------------------------------------

    if prev_snapshot is not None:
        prev_loop = (prev_snapshot.get("sensor_readings", {})
                                  .get("LOOP_DATA", {}) or {})
        prev_count = prev_loop.get("Loop_Vehicle_Count") or 0

        if loop_count is not None and prev_count is not None:
            diff = loop_count - prev_count
            ratio = (loop_count / prev_count) if prev_count > 0 else None

            if (
                diff > EDGE_SPIKE_ABS and
                (ratio is not None and ratio > EDGE_SPIKE_RATIO)
            ):
                add(
                    "EDGE_SPIKE_SPOOF",
                    (
                        "Sudden spike in loop vehicle count: "
                        f"prev={prev_count}, curr={loop_count}, diff={diff}, "
                        f"ratio={ratio:.2f}. Possible spoofed edge data."
                    ),
                    severity="CRITICAL",
                    attack=True,
                )

    # -------------------------------------------------
    # 5. FORCED ALL-RED DoS
    # -------------------------------------------------

    is_all_red_flag = loop.get("Is_All_Red") == 1
    queue_len = cam.get("Queue_Length") or 0
    emergency = rcu.get("Emergency_Flag") or 0
    preempt_calls = rcu.get("Preempt_Call_Count") or 0

    all_lights_red = all(
        light_state.get(d) == "RED"
        for d in ("N", "S", "E", "W")
        if d in light_state
    )

    if (phase == "ALL_RED" or is_all_red_flag or all_lights_red) and \
       emergency == 0 and preempt_calls == 0 and \
       queue_len >= ALL_RED_QUEUE_THRESHOLD:
        add(
            "FORCED_ALL_RED_DOS",
            (
                "Intersection appears to be stuck in all-red state "
                f"without emergency (Queue_Length={queue_len}). "
                "Possible DoS forcing all-red."
            ),
            severity="CRITICAL",
            attack=True,
        )

    # -------------------------------------------------
    # 6. Camera vs loop consistency (generic anomalies)
    # -------------------------------------------------

    if cam_speed is not None and loop_speed is not None:
        if (abs(cam_speed - loop_speed) > 10 and
                max(cam_speed, loop_speed) / max(min(cam_speed, loop_speed), 1) > 2):
            add(
                "CAMERA_LOOP_SPEED_MISMATCH",
                f"Camera speed={cam_speed}, Loop speed={loop_speed} (large difference)",
                severity="WARN",
            )

    if loop_count is not None and total_cam_cars > 0:
        ratio = loop_count / max(total_cam_cars, 1)
        if ratio > 3 or ratio < 0.3:
            add(
                "CAMERA_LOOP_COUNT_MISMATCH",
                f"Camera total={total_cam_cars}, Loop count={loop_count} (ratio={ratio:.2f})",
                severity="WARN",
            )

    return anomalies


def classify_status(anomalies: List[Dict[str, Any]]) -> str:
    """
    Decide high-level status:
    - OK
    - ANOMALY
    - ATTACK_SUSPECTED
    """
    if not anomalies:
        return "OK"

    if any(a.get("is_attack_suspected") for a in anomalies):
        return "ATTACK_SUSPECTED"

    return "ANOMALY"
