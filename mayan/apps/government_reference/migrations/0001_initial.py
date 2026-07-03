from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='GovernmentReferenceSequence',
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True,
                        serialize=False, verbose_name='ID'
                    )
                ),
                (
                    'ministry', models.CharField(
                        max_length=16, verbose_name='Ministry'
                    )
                ),
                (
                    'department', models.CharField(
                        max_length=32, verbose_name='Department'
                    )
                ),
                (
                    'year', models.PositiveIntegerField(verbose_name='Year')
                ),
                (
                    'last_sequence', models.PositiveIntegerField(
                        default=0, verbose_name='Last sequence'
                    )
                ),
                (
                    'created_at', models.DateTimeField(
                        auto_now_add=True, verbose_name='Created at'
                    )
                ),
                (
                    'updated_at', models.DateTimeField(
                        auto_now=True, verbose_name='Updated at'
                    )
                )
            ],
            options={
                'ordering': ('ministry', 'department', 'year'),
                'verbose_name': 'Government reference sequence',
                'verbose_name_plural': 'Government reference sequences',
                'unique_together': {('ministry', 'department', 'year')}
            }
        )
    ]
