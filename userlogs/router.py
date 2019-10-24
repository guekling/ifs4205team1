"""
See https://docs.djangoproject.com/en/2.2/topics/db/multi-db/#topics-db-multi-db-routing for details on db reouters.
"""

class UserlogsRouter(object):
    """
    A router to control all database operations on models in the logtransactions application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read userlogs models go to logdb.
        """
        if model._meta.app_label == 'userlogs':
            return 'logdb'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write userlogs models go to logdb.
        """
        if model._meta.app_label == 'userlogs':
            return 'logdb'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both models are in userlogs app
        """
        if obj1._meta.app_label == 'userlogs' and obj2._meta.app_label == 'userlogs':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure the userlogs app only appears in the 'logdb' database.
        """
        if app_label == 'userlogs':
            return db == 'logdb'
        return None