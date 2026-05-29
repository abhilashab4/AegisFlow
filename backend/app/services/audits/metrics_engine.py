import json
from pathlib import Path


LOG_FILE = "audit_logs.jsonl"


class MetricsEngine:

    def __init__(self):

        self.log_path = Path(LOG_FILE)


    def load_logs(self):

        if not self.log_path.exists():
            return []

        with open(self.log_path, "r") as f:

            return [
                json.loads(line)
                for line in f.readlines()
            ]


    def compute_metrics(self):

        logs = self.load_logs()

        total_requests = len(logs)

        blocked_requests = 0

        pii_detections = 0

        residual_pii_failures = 0

        for log in logs:

            metadata = log.get(
                "metadata",
                {}
            )

            if metadata.get("blocked"):
                blocked_requests += 1

            pii_detections += len(
                metadata.get(
                    "detections",
                    []
                )
            )

            if metadata.get(
                "residual_pii_detected"
            ):
                residual_pii_failures += 1



        block_rate = (
            blocked_requests / total_requests
            if total_requests else 0
        )

        pii_redaction_rate = (
            1 -
            (
                residual_pii_failures /
                total_requests
            )
            if total_requests else 0
        )

        false_negative_rate = (
            residual_pii_failures /
            total_requests
            if total_requests else 0
        )

        return {

            "total_requests":
                total_requests,

            "blocked_requests":
                blocked_requests,

            "block_rate":
                round(block_rate, 3),

            "pii_detections":
                pii_detections,

            "pii_redaction_rate":
                round(
                    pii_redaction_rate,
                    3
                ),

            "false_negative_rate":
                round(
                    false_negative_rate,
                    3
                ),

            "MTTD":
                "Real-time",

            "MTTR":
                "Automated"
        }