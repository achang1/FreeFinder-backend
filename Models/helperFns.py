import decimal, datetime
from sqlalchemy import DateTime

# metadata.create_all(engine)
#Usage: json.dumps([dict(r) for r in res], default=alchemyencoder)
def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, (datetime, DateTime)):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)