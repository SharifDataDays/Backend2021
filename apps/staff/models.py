from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO
import sys


class Team(models.Model):
    title_en = models.CharField(max_length=50, blank=True)
    title_fa = models.CharField(max_length=50)
    order = models.IntegerField(default=0)

    def __str__(self):
        return '%s' % (self.title_fa)


class SubTeam(models.Model):
    title_en = models.CharField(max_length=50, blank=True)
    title_fa = models.CharField(max_length=50)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='subteams', null=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return '%s' % (self.title_fa)


class Staff(models.Model):
    subteam = models.ForeignKey(
        SubTeam, on_delete=models.CASCADE, related_name='staffs')

    image = models.ImageField()
    title_en = models.CharField(max_length=50, blank=True)
    title_fa = models.CharField(max_length=50, blank=True)
    name_en = models.CharField(max_length=50, blank=True)
    name_fa = models.CharField(max_length=50)
    link = models.URLField(max_length=400, null=True, blank=True)
    description = models.TextField(max_length=400, null=True, blank=True)
    order = models.IntegerField(default=1, blank=True)
    
    def compress_image(self, staff_pic):
        tmp_image = Image.open(staff_pic)

        tmp_image = tmp_image.convert('RGB')
        new_width = 300
        new_height = new_width * tmp_image.height // tmp_image.width
        tmp_image = tmp_image.resize((new_width, new_height))

        output_stream = BytesIO()
        tmp_image.save(output_stream, format='JPEG', quality=300)
        output_stream.seek(0)
        staff_pic = InMemoryUploadedFile(output_stream, 'ImageField', "{}.jpg".format(staff_pic.name.split('.')[0]), 'image/jpeg', sys.getsizeof(output_stream), None)
        return staff_pic

    def save(self, *args, **kwargs):
        if not self.id:
            self.image = self.compress_image(self.image)
        super(Staff, self).save(*args, **kwargs)

    def __str__(self):
        return '%s' % (self.name_fa)

