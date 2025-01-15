from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import User

@registry.register_document
class UserDocument(Document):
    email = fields.KeywordField()
    class Index:
        name = 'users'

    class Django:
        model = User
        fields = []