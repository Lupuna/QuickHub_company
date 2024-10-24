from django.contrib import admin
from company.models import Company, Position, ProjectPosition, Project


admin.site.register(Company)
admin.site.register(Position)
admin.site.register(ProjectPosition)
admin.site.register(Project)

