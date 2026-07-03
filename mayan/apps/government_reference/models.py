from django.db import models
from django.utils.translation import gettext_lazy as _


class GovernmentReferenceSequence(models.Model):
    ministry = models.CharField(
        max_length=16, verbose_name=_(message='Ministry')
    )
    department = models.CharField(
        max_length=32, verbose_name=_(message='Department')
    )
    year = models.PositiveIntegerField(verbose_name=_(message='Year'))
    last_sequence = models.PositiveIntegerField(
        default=0, verbose_name=_(message='Last sequence')
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_(message='Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_(message='Updated at')
    )

    class Meta:
        ordering = ('ministry', 'department', 'year')
        unique_together = ('ministry', 'department', 'year')
        verbose_name = _(message='Government reference sequence')
        verbose_name_plural = _(message='Government reference sequences')

    def __str__(self):
        return '{}/{}/{}'.format(
            self.ministry, self.department, self.year
        )
