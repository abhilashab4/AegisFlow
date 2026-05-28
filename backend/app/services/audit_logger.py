import json
import logging
import aiofiles
from datetime import datetime

logger = logging.getLogger(__name__)

async def log_request(data: dict):

    try:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": data.get("request_id"),
            "user": data.get("username"),
            "dept": data.get("dept", "general"), 
            "original_prompt": data.get("original_prompt"),
            "sanitized_prompt": data.get("sanitized_prompt"),
            "blocked": data.get("blocked", False),
            "reason": data.get("reason"),
            "category": data.get("category"),     
        }

        async with aiofiles.open("audit_logs.jsonl", mode='a') as f:
            await f.write(json.dumps(log_entry) + "\n")
            
    except Exception as e:
        logger.error(f"Audit log writing failed: {str(e)}")