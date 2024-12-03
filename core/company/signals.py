from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from company.models import Company, Position, Project, ProjectPosition
from rest_framework.exceptions import ValidationError

from jwt_registration.models import User


@receiver(m2m_changed, sender=Company.users.through)
def create_company_position(instance, action, **kwargs):
    user_creator_id = list(kwargs.get('pk_set', []))[0]
    if action == 'pre_add':
        creator = User.objects.get(id=user_creator_id)
        creators_company_with_same_title = Company.objects.filter(
            title=instance.title, users=creator).exclude(id=instance.id)
        creators_positions_list = Position.objects.filter(
            company__in=creators_company_with_same_title).values_list('access_weight')
        if (0,) in creators_positions_list:
            instance.delete()
            raise ValidationError({'error': 'data_update is required'})
    if action == 'post_add':
        user_creator_id = list(kwargs.get('pk_set', []))[0]
        creator = User.objects.get(id=user_creator_id)
        if user_creator_id:
            position = Position.objects.filter(company=instance).first()
            if position is None:
                position = Position.objects.create(company=instance)
                position.users.add(user_creator_id)


@receiver(post_save, sender=Project)
def create_project_position(sender, instance, created, **kwargs):
    if created:
        company_positions = Position.objects.filter(company=instance.company)
        project_positions = [
            ProjectPosition(project=instance, position=position)
            for position in company_positions
        ]

        ProjectPosition.objects.bulk_create(project_positions)
