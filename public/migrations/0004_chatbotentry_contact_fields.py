from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("public", "0003_collectedmessage"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatbotentry",
            name="email_address",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="chatbotentry",
            name="phone_number",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="chatbotentry",
            name="whatsapp_number",
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
