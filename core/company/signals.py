from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from company.models import Company, Position


@receiver(m2m_changed, sender=Company.users.through)
def create_company_position(sender, instance, action, **kwargs):
    if action == 'post_add':
        users_to_add = kwargs.get('pk_set', [])
        if users_to_add:
            position, created = Position.objects.get_or_create(company=instance)
            if created:
                position.users.add(*users_to_add)
