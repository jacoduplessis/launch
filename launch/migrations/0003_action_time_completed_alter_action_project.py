# Generated by Django 4.2.7 on 2023-11-06 05:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("launch", "0002_action"),
    ]

    operations = [
        migrations.AddField(
            model_name="action",
            name="time_completed",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="action",
            name="project",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="actions", to="launch.project"),
        ),
    ]
