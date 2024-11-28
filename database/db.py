from contextlib import contextmanager
from sqlalchemy.exc import OperationalError
from database.models import Session
import time

@contextmanager
def db_session(max_retries=3, delay=1):
    retries = 0
    while True:
        try:
            session = Session()
            try:
                yield session
                session.commit()
                break
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
        except OperationalError as e:
            retries += 1
            if retries >= max_retries:
                raise e
            time.sleep(delay)
            continue