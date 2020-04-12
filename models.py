from django.db import models


class Genre(models.Model):
    name = models.CharField(
            verbose_name='Genre',
            max_length=255,
            unique=True,
            )
    
    def __str__(self):
        return self.name


class Concert(models.Model):
    detail_url = models.CharField(
            verbose_name='URL for Concert Detail Page',
            max_length=255,
            unique=True,
            )
    title = models.CharField(
            verbose_name='Concert Title',
            max_length=255,
            unique=True,
            )
    location = models.CharField(
            verbose_name='Concert Location',
            max_length=255,
            )
    start_date = models.DateField(
            verbose_name='Concert Start Date',
            )
    end_date = models.DateField(
            verbose_name='Concert End Date',
            )
    is_opened = models.BooleanField(
            verbose_name='Is Concert Ticketing Opened?',
            )
    open_time = models.DateTimeField(
            verbose_name='Concert Ticketing Opening Time (only for not opened concerts)',
            null=True,
            )

    def __str__(self):
        return self.title


class ConcertGenre(models.Model):
    concert = models.ForeignKey(
            verbose_name='Concert',
            to='Concert',
            on_delete=models.CASCADE,
            )
    genre = models.ForeignKey(
            verbose_name='Genre',
            to='Genre',
            on_delete=models.CASCADE,
            )
    priority = models.IntegerField(
            verbose_name='Genre Priority',
            )

    def __str__(self):
        return self.concert.title + ': ' + self.genre.name


class Artist(models.Model):
    name = models.CharField(
            verbose_name = 'Artist Name',
            max_length=255,
            unique=True,
            )
    genre = models.ForeignKey(
            verbose_name='Artist Genre',
            to='Genre',
            on_delete=models.CASCADE,
            )

    def __str__(self):
        return self.name


class ConcertArtist(models.Model):
    concert = models.ForeignKey(
            verbose_name='Concert',
            to='Concert',
            on_delete=models.CASCADE,
            )
    artist = models.ForeignKey(
            verbose_name='Artist',
            to='Artist',
            on_delete=models.CASCADE,
            )

    def __str__(self):
        return self.concert.title + ': ' + self.artist.name


class Price(models.Model):
    price_type = models.CharField(
            verbose_name='Price Type',
            max_length=255,
            )
    price = models.IntegerField(
            verbose_name='Price',
            )
    concert = models.ForeignKey(
            verbose_name='Concert',
            to='Concert',
            on_delete=models.CASCADE,
            )

    def __str__(self):
        return self.concert.title + ': ' + self.price_type + ' ' + str(self.price) + '원'

