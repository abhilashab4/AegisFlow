import json
import hashlib
from datetime import datetime
from pathlib import Path


LOG_FILE = "audit_logs.jsonl"


class AuditLogger:

    def __init__(self):

        self.log_path = Path(LOG_FILE)


    def generate_hash(self, data: dict):

        serialized = json.dumps(
            data,
            sort_keys=True
        ).encode()

        return hashlib.sha256(
            serialized
        ).hexdigest()


    def get_previous_hash(self):

        if not self.log_path.exists():
            return "GENESIS_HASH"

        with open(self.log_path, "r") as f:

            lines = f.readlines()

            if not lines:
                return "GENESIS_HASH"

            last_entry = json.loads(
                lines[-1]
            )

            return last_entry["current_hash"]


    def log_event(
        self,
        event_type: str,
        actor: str,
        metadata: dict
    ):

        previous_hash = (
            self.get_previous_hash()
        )

        entry = {

            "timestamp":
                datetime.utcnow().isoformat(),

            "event_type":
                event_type,

            "actor":
                actor,

            "metadata":
                metadata,

            "previous_hash":
                previous_hash
        }

        current_hash = (
            self.generate_hash(entry)
        )

        entry["current_hash"] = (
            current_hash
        )

        with open(self.log_path, "a") as f:

            f.write(
                json.dumps(entry) + "\n"
            )

        return entry

    def verify_chain(self):

        if not self.log_path.exists():

            return {
                "valid": True,
                "message": "No audit log found"
            }

        with open(self.log_path, "r") as f:

            lines = f.readlines()

        previous_hash = "GENESIS_HASH"

        for index, line in enumerate(lines):

            entry = json.loads(line)

            stored_hash = entry["current_hash"]

            verification_entry = dict(entry)

            del verification_entry["current_hash"]

            recalculated_hash = (
                self.generate_hash(
                    verification_entry
                )
            )

            if stored_hash != recalculated_hash:

                return {
                    "valid": False,
                    "error":
                        f"Hash mismatch at "
                        f"log index {index}"
                }

            if entry["previous_hash"] != previous_hash:

                return {
                    "valid": False,
                    "error":
                        f"Chain broken at "
                        f"log index {index}"
                }

            previous_hash = stored_hash

        return {
            "valid": True,
            "message":
                "Audit chain verified successfully"
        }