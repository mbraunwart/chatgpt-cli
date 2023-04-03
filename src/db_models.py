from sqlalchemy import (
    Column,
    Integer,
    String,
    LargeBinary,
    DateTime,
    ForeignKey,
    create_engine,
    desc,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class UserSession(Base): # type: ignore
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("history_topics.id"))
    topic = relationship("HistoryTopic", back_populates="sessions")
    last_active = Column(DateTime, default=None)


class HistoryTopic(Base): # type: ignore
    __tablename__ = "history_topics"

    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    model = Column(String(200))
    messages = relationship("Message", back_populates="history_topic")
    sessions = relationship(
        "UserSession", back_populates="topic", cascade="all, delete-orphan"
    )


class Message(Base): # type: ignore
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    prompt = Column(LargeBinary)
    history_topic_id = Column(
        Integer,
        ForeignKey("history_topics.id"),
    )
    created_date = Column(DateTime(timezone=True))

    history_topic = relationship("HistoryTopic", back_populates="messages")
