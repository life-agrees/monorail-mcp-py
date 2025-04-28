from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy import Column, JSON

class FailedTrade(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pair: str = Field(index=True)
    payload: dict = Field(sa_column=Column(JSON))
    error: str
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="UTC timestamp of failure"
    )

# SQLite database URL (file 'trades.db' in project root)
DATABASE_URL = "sqlite:///./trades.db"
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    """
    Initialize the database and create tables.
    """
    SQLModel.metadata.create_all(engine)


def save_failure(record: dict) -> int:
    """
    Persist a failed trade record to the database.

    Args:
        record: Dict with keys 'pair', 'payload', 'error'.

    Returns:
        The ID of the created FailedTrade record.
    """
    with Session(engine) as session:
        ft = FailedTrade(
            pair=record["pair"],
            payload=record["payload"],
            error=record["error"]
            # timestamp omitted so default_factory applies
        )
        session.add(ft)
        session.commit()
        session.refresh(ft)
        return ft.id


def get_all_failures() -> List[FailedTrade]:
    """
    Retrieve all failed trades, most recent first.

    Returns:
        List of FailedTrade instances.
    """
    with Session(engine) as session:
        statement = select(FailedTrade).order_by(FailedTrade.timestamp.desc())
        return session.exec(statement).all()
