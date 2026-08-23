from sqlalchemy import select
from app.models.company_policy import Policy


class PolicyService:
    def __init__(self, db, embedding_service):
        self.db = db
        self.embedding_service = embedding_service

    async def find_matching_policy(self, text: str):
        
        embedding = self.embedding_service.encode(text)

        distance = Policy.embedding.cosine_distance(embedding)

        query = (
            select(Policy, distance.label("distance"))
            .where(Policy.enabled.is_(True))
            .order_by(distance)
            .limit(1)
        )

        result = await self.db.execute(query)

        row = result.first()

        if not row:
            return None

        policy, distance_value = row

        similarity = 1 - float(distance_value)

        return {
            "category": policy.category,
            "description": policy.description,
            "severity": policy.severity,
            "threshold": policy.threshold,
            "action": policy.action,
            "similarity": similarity,
        }