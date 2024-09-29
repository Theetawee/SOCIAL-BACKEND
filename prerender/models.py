from django.db import models


class ScrapedContent(models.Model):
    url = models.URLField(unique=True)
    content = models.TextField()
    scraped_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.url)
