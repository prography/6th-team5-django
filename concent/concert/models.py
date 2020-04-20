from django.db import models


# 티켓팅 사이트 일단 있는 대로 추가 (나중에 넣으려면 귀찮)
TICKETING_SITES = (
        ('Inpark', 'Interpark', ),
        ('Melon', 'Melon', ),
        ('Yes24', 'Yes24', ),
        ('Link', 'Ticketlink', ),
        ('Auction', 'Auction', ),
        ('Hana', 'Hanaticket', ),
        )

# 장르는 지금 사용하지는 않으나 미래를 위해 필드는 만들어둠
# 가장 우선순위가 높은 2개의 티켓팅 사이트 기준
# 인터파크티켓 : Ballad / Rock / Hiphop / Jazz,RnB / Trot,Folk / Foreign / Indie
# (Elec, Dance 없음. Festival은 모두 수작업)
# 멜론티켓 : Dance / Ballad,RnB / Hiphop,Elec / Indie,Rock / Foreign / Jazz,Trot,Folk
# (Festival 중 타 장르 미분류는 수작업)
GENRES = (
        ('BalRnB', 'Ballad/RnB', ),
        ('Dance', 'Dance', ),
        ('RockInd', 'Rock/Indie', ),
        ('HipElec', 'Hiphop/Elec', ),
        ('Others', 'Jazz/Trot/Folk', ),
        ('Foreign', 'Foreign', ),
        )


class Artist(models.Model):
    artist_name = models.CharField(
            verbose_name='Artist Name',
            max_length=63,
            # 동명이인은 뒤에 괄호를 붙이든가 하자...
            unique=True, 
            )
    # 아티스트 장르는 가져오게 된다면 멜론에서? 나중에 생각하기
    artist_genre = models.CharField(
            verbose_name='Artist Genre',
            choices=GENRES,
            max_length=15,
            null=True,
            )

    def __str__(self):
        return self.artist_name


class Concert(models.Model):
    info_source = models.CharField(
            verbose_name='Info Source Site',
            choices=TICKETING_SITES,
            max_length=15,
            )
    detail_url = models.CharField(
            verbose_name='Detail Page URL',
            max_length=255,
            )
    artists = models.ManyToManyField(
            verbose_name='Artists in Concert',
            to=Artist,
            )
    concert_name = models.CharField(
            verbose_name='Concert Name',
            max_length=127,
            unique=True,
            )
    location = models.CharField(
            verbose_name='Concert Location',
            max_length=31,
            )
    address = models.CharField(
            verbose_name='Concert Location Address',
            max_length=255,
            null=True,
            )
    start_date = models.DateField(
            verbose_name='Concert Starting Date',
            )
    end_date = models.DateField(
            verbose_name='Concert Ending Date',
            )
    is_opened = models.BooleanField(
            verbose_name='Is Ticket Opened?',
            )
    open_time = models.DateTimeField(
            verbose_name='Ticket Opening Time',
            null=True,
            )

    def __str__(self):
        return self.concert_name


class Price(models.Model):
    concert = models.ForeignKey(
            verbose_name='Concert',
            to='Concert',
            on_delete=models.CASCADE,
            )
    price_type = models.CharField(
            verbose_name='Price Type',
            max_length=31,
            unique=True,
            )
    price = models.IntegerField(
            verbose_name='Price',
            )
    
    # example: 그린플러그드 서울 2020 - 양일권 88000원
    def __str__(self):
        return self.concert.concert_name + ' - ' + self.price_type + ' ' + str(self.price) + '원'

