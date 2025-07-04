# Generated by Django 5.0.6 on 2025-05-17 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('degusta_rioApp', '0003_restaurante_foto'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurante',
            name='avaliacao',
            field=models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurante',
            name='descricao',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Comentario',
        ),
    ]
