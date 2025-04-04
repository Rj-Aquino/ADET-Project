from django.db import models

# Create your models here.
class UserInput(models.Model):
    query_text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query_text

class ResearchPaper(models.Model):
    input = models.ForeignKey(UserInput, on_delete=models.CASCADE, related_name='recommendations')
    title = models.CharField(max_length=255)
    abstract = models.TextField(blank=True, null=True)
    authors = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    source = models.CharField(max_length=50, choices=[('Pinecone', 'Pinecone'), ('EXA', 'EXA')])
    score = models.FloatField()
    year = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title