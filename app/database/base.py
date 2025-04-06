from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


from app.data_sources.strong.models import *
from app.data_sources.amazon.kindle.models import *
from app.data_sources.google.fitbit.models import *
