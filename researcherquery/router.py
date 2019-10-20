"""
See https://docs.djangoproject.com/en/2.2/topics/db/multi-db/#topics-db-multi-db-routing for details on db reouters.
"""

class ResearcherqueryRouter(object):
    """
    A router to control all database operations on models in the researcherquery application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read researcherquery models go to safedb.
        """
        if model._meta.app_label == 'researcherquery':
            return 'safedb'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write researcherquery models go to safedb.
        """
        if model._meta.app_label == 'researcherquery':
            return 'safedb'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both models are in researcherquery app
        """
        if obj1._meta.app_label == 'researcherquery' and obj2._meta.app_label == 'researcherquery':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure the researcherquery app only appears in the 'safedb' database.
        """
        if app_label == 'researcherquery':
            return db == 'safedb'
        return None