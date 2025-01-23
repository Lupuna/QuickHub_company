from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from company.models import Company, Position, Project, ProjectPosition
from rest_framework.exceptions import ValidationError

from jwt_registration.models import User


@receiver(m2m_changed, sender=Company.users.through)
def create_company_position(instance, action, sender, **kwargs):
    if action == 'pre_add':
        users_pk = list(kwargs.get('pk_set', []))
        company_is_new = not sender.objects.filter(
            company_id=instance.id).exists()
        creator = User.objects.filter(id=users_pk[0])
        if company_is_new and len(users_pk) == 1:
            creators_company_with_same_title = Company.objects.filter(
                title=instance.title, users__in=creator).exclude(id=instance.id)
            creators_positions_list = Position.objects.filter(
                company__in=creators_company_with_same_title).values_list('access_weight', flat=True)
            if 1 in creators_positions_list:
                instance.delete()
                raise ValidationError({'error': 'data_update is required'})

    if action == 'post_add':
        sender_objs = sender.objects.filter(company_id=instance.id)
        company_is_new = len(sender_objs) == 1
        if company_is_new:
            creator = User.objects.get(id=sender_objs[0].user_id)
            position = Position.objects.create(company=instance)
            position.users.add(creator)


@receiver(post_save, sender=Project)
def create_project_position(sender, instance, created, **kwargs):
    if created:
        company_positions = Position.objects.filter(company=instance.company)
        project_positions = [
            ProjectPosition(project=instance, position=position)
            for position in company_positions
        ]

        ProjectPosition.objects.bulk_create(project_positions)
