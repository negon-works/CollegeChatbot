from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("public", "0002_chatbotentry_category"),
    ]

    operations = [
        migrations.CreateModel(
            name="CollectedMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question", models.CharField(max_length=255, unique=True)),
                ("count", models.PositiveIntegerField(default=1)),
                ("is_processed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["is_processed", "-count", "-updated_at", "-id"],
            },
        ),
    ]
