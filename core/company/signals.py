from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from company.models import Company, Position, Project, ProjectPosition


@receiver(m2m_changed, sender=Company.users.through)
def create_company_position(sender, instance, action, **kwargs):
    if action == 'post_add':
        users_to_add = kwargs.get('pk_set', [])
        if users_to_add:
            position = Position.objects.filter(company=instance).first()
            if position is None:
                position = Position.objects.create(company=instance)
                position.users.add(*users_to_add)


@receiver(post_save, sender=Project)
def create_project_position(sender, instance, created, **kwargs):
    if created:
        company_positions = Position.objects.filter(company=instance.company)
        project_positions = [
            ProjectPosition(project=instance, position=position)
            for position in company_positions
        ]

        ProjectPosition.objects.bulk_create(project_positions)
