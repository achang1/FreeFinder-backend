from sqlalchemy import create_engine, Float, DateTime, MetaData, Table, Column, Integer, String, ForeignKey, Sequence
from datetime import datetime

engine = create_engine('mysql://freefinder_admin:test123@70.79.100.163/ff_db')
conn = engine.connect()

metadata = MetaData()

users = Table('users', metadata,
    Column('id', Integer, Sequence('user_id_seq'), primary_key=True),
    Column('email', String(50), nullable=False, unique=True),
    Column('name', String(50), nullable=False),
    Column('password', String(255), nullable=False),
    Column('phone', String(50)),
    Column('location', String(50)),
)

posts = Table('posts', metadata,
    Column('id', Integer, Sequence('post_id_seq'), primary_key=True),
    Column('user_id', Integer, ForeignKey("users.id"), nullable=False),
    Column('title', String(50), nullable=False),
    Column('time', DateTime, nullable=False),
    Column('expiry', DateTime),
    Column('last_modified', DateTime, onupdate=datetime.now(), nullable=False),
    Column('description', String(5000), nullable=False),
    Column('location', String(50), nullable=False),
    Column('lat', Float),
    Column('lon', Float),
)

comments = Table('comments', metadata,
    Column('id', Integer, Sequence('comment_id_seq'), primary_key=True),
    Column('post_id', Integer, ForeignKey("posts.id"), nullable=False),
    Column('user_id', Integer, ForeignKey("users.id"), nullable=False),
    Column('text_body', String(5000), nullable=False),
    Column('date', DateTime, nullable=False),
)