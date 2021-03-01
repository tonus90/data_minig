from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models
"""
get or create либой дай либо верни (дай или создай)
"""

class Database:

    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    def _get_or_create(self, session, model, **data):
        db_data = session.query(model).filter(model.url == data['url']).first()
        if not db_data:
            db_data = model(**data)
        return db_data



    def create_post(self, data):
        session = self.maker()
        author = self._get_or_create(session, models.Author, **data['author_data'])
        tags = map(lambda tag_data: self._get_or_create(session, models.Tag, **tag_data), data['tags_data'])
        post = self._get_or_create(session, models.Post, **data['post_data'], author=author)
        post.tags.extend(tags)
        session.add(post)

        try:
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()
        print(1)
