from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("public", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatbotentry",
            name="category",
            field=models.CharField(
                choices=[("chatbot", "Chatbot"), ("college", "College")],
                default="college",
                max_length=20,
            ),
        ),
        migrations.AlterModelOptions(
            name="chatbotentry",
            options={"ordering": ["category", "priority", "intent", "id"]},
        ),
    ]
