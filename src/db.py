from datetime import datetime, timedelta
from typing import List, Optional, TypeVar, Type, cast
from db_models import Base, UserSession
from sqlalchemy import (
    create_engine,
    desc,
)
from sqlalchemy.orm import sessionmaker, Session

T = TypeVar("T")

class Database:
    DATABASE_URL = "sqlite:///chatgpt_cli.db"
    engine = create_engine(DATABASE_URL)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def init_db(self) -> None:
        Base.metadata.create_all(bind=Database.engine)

    def add(self, session: Session, item: T) -> T:
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    def get_all(self, session: Session, entity: Type[T]) -> List[T]:
        return session.query(entity).all()

    def get_by_id(self, session: Session, entity: Type[T], id: int) -> Optional[T]:
        return cast(Optional[T], session.query(entity).get(id))  # type: ignore

    def get_latest(self, session: Session, entity: Type[T]) -> Optional[T]:
        return session.query(entity).order_by(desc(getattr(entity, "id"))).first()

    def update(self, session: Session, item: T) -> T:
        session.commit()
        return item

    def delete(self, session: Session, item: T) -> None:
        session.delete(item)
        session.commit()

    def create_user_session(self) -> UserSession:
        user_session = UserSession(last_active=datetime.now())
        self.add(self.SessionLocal(), user_session)
        return user_session

    def get_user_session_by_topic_id(self, topic_id: int) -> Optional[UserSession]:
        return (
            self.SessionLocal()
            .query(UserSession)
            .filter(UserSession.topic_id == topic_id)
            .first()
        )

    def get_active_user_session(self, hours: int = 24) -> Optional[UserSession]:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return (
            self.SessionLocal()
            .query(UserSession)
            .filter(UserSession.last_active >= cutoff_time)
            .order_by(UserSession.last_active.desc())
            .first()
        )
