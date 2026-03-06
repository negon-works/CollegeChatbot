from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChatbotEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intent', models.CharField(max_length=80)),
                ('trigger_keywords', models.TextField(help_text='Comma or new-line separated keywords (example: fees, fee structure, course fee)')),
                ('response', models.TextField()),
                ('follow_up', models.TextField(blank=True)),
                ('priority', models.PositiveIntegerField(default=100)),
                ('is_active', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['priority', 'intent', 'id'],
            },
        ),
    ]
