"""Service layer.

Services encapsulate business rules and database access so that routers stay
thin. Each service raises :class:`fastapi.HTTPException` with the appropriate
status code on error, keeping HTTP concerns close to the operation that knows
why it failed.
"""
