from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from jwt_registration.models import User
from .models import Company, Project

@registry.register_document
class CompanyDocument(Document):
    users = fields.NestedField(properties={
        'email': fields.KeywordField()
    })

    class Index:
        name = 'companies'

    class Django:
        model = Company
        fields = [
            'title',
        ]
        #related_models = [User]



@registry.register_document
class ProjectDocument(Document):
    users = fields.NestedField(properties={
        'email': fields.KeywordField()
    })

    class Index:
        name = 'projects'

    class Django:
        model = Project
        fields = [
            'title',
        ]
        #related_models = [User]

