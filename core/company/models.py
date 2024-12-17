from django.core.validators import MaxValueValidator
from django.db import models
from jwt_registration.models import User
from django.utils.translation import gettext_lazy as _
import random


class Company(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    users = models.ManyToManyField(
        User, related_name='companies',
        help_text=_('connection with User')
    )

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
        ordering = ['title']

    def __str__(self):
        return self.title


class Position(models.Model):
    class WeightChoices(models.IntegerChoices):
        OWNER = 0, _('Owner')
        FULL_ACCESS = 1, _('Setting up project parameters')
        PARTIAL_ACCESS = 2, _('Executing and assigning tasks')
        MINIMUM_ACCESS = 3, _('Executing tasks')
        OBSERVE = 4, _('Observer')

    title = models.CharField(max_length=255, default=_('Owner'))
    description = models.TextField(null=True, blank=True)
    access_weight = models.PositiveSmallIntegerField(
        choices=WeightChoices.choices,
        default=WeightChoices.OWNER,
        help_text=_("access level for the position")
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        related_name='positions',
        help_text=_('connection with Company')
    )
    users = models.ManyToManyField(
        User, related_name='positions',
        help_text=_('connection with User')
    )
    projects = models.ManyToManyField(
        'Project', through='ProjectPosition',
        related_name='positions',
        help_text=_('connection with Project')
    )

    class Meta:
        verbose_name = _("Position")
        verbose_name_plural = _("Positions")
        ordering = ['access_weight']

    def __str__(self):
        return self.title


class ProjectPosition(models.Model):
    class WeightChoices(models.IntegerChoices):
        FULL_ACCESS = 1, _('Setting up project parameters')
        PARTIAL_ACCESS = 2, _('Executing and assigning tasks')
        MINIMUM_ACCESS = 3, _('Executing tasks')
        OBSERVE = 4, _('Observer')
        STANDARD = 5, _('Standard')

    project_access_weight = models.PositiveSmallIntegerField(
        choices=WeightChoices.choices,
        default=WeightChoices.STANDARD,
        help_text=_("access level for the position")
    )

    position = models.ForeignKey(
        Position, on_delete=models.CASCADE, related_name='project_positions')
    project = models.ForeignKey(
        'Project', on_delete=models.CASCADE, related_name='position_projects')

    class Meta:
        verbose_name = _("Project Position")
        verbose_name_plural = _("Project Positions")

    def __str__(self):
        return f"{self.position.title} - {self.project.title}"


class Project(models.Model):
    class Priority(models.IntegerChoices):
        HIGH = 0, 'High'
        MEDIUM = 1, 'Medium'
        LOW = 2, 'Low'

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        related_name='projects',
        help_text=_('connection with Company')
    )
    users = models.ManyToManyField(
        User, related_name='projects',
        help_text=_('connection with User')
    )
    departments = models.ManyToManyField(
        'Department', related_name='departments',
        help_text=_('connection with Department'),
    )
    color = models.CharField(
        max_length=20,
        default=f'rgb({random.randint(150, 220)},{random.randint(150, 220)},{random.randint(150, 220)})'
    )
    priority = models.PositiveSmallIntegerField(
        choices=Priority.choices, default=Priority.MEDIUM,
        validators=[MaxValueValidator(5)]
    )
    creation_date = models.DateField(auto_now_add=True, editable=False)
    date_of_update = models.DateField(auto_now=True)
    owner = models.EmailField(null=True, blank=True)

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['title']

    def __str__(self):
        return self.title


class Department(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        related_name='departments',
        help_text=_('connection with Company')
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='children',
        help_text=_('connection with department parent')
    )
    color = models.CharField(
        max_length=20,
        default=f'rgb({random.randint(150, 220)},{random.randint(150, 220)},{random.randint(150, 220)})'
    )
    users = models.ManyToManyField(
        User, related_name='departments',
        help_text=_('connection with User')
    )
    owner = models.EmailField(null=True, blank=True)

    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")

    def __str__(self):
        return self.title
