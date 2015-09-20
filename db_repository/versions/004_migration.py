from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
file = Table('file', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('owner', INTEGER),
    Column('title', VARCHAR),
    Column('path', VARCHAR),
    Column('parent', VARCHAR),
    Column('last_modified', DATETIME),
)

file = Table('file', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('owner_id', Integer),
    Column('title', String),
    Column('path', String),
    Column('parent', String),
    Column('last_modified', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['file'].columns['owner'].drop()
    post_meta.tables['file'].columns['owner_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['file'].columns['owner'].create()
    post_meta.tables['file'].columns['owner_id'].drop()
