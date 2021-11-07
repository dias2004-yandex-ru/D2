from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


# Create your models here.
# Author - все авторы. Связи: Author-1:1-User
class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)         # наименование автора == пользователь
    authorRating = models.SmallIntegerField(default=0)                        # рейтинг автора

    def update_rating(self):        # расчёт рейтинга автора
        # суммарный рейтинг всех статей автора:
        postRtng = self.post_set.all().aggregate(pR=Sum('postRating'))
        pRtng = 0
        pRtng += postRtng.get('pR')

        # суммарный рейтинг всех комментариев автора:
        commentRtng = self.authorUser.comment_set.all().aggregate(cR=Sum('commentRating'))
        cRtng = 0
        cRtng += commentRtng.get('cR')

        # суммарный рейтинг всех комментариев ко всем статьям автора:
        #ovrlRtng = self.post.comment... не придумал, как сформулировать.
        # в shell работает запрос (например, для authorUser__username='user1')
        #Comment.objects.filter(commentPost__postAuthor__authorUser__username='user1').aggregate(Sum('commentRating'))
        # а здесь - ?

        # итоговый рейтинг автора
        self.authorRating = 3*pRtng + cRtng
        self.save()


# категория статьи|новости: каждую статью можно отнести к нескольким категориям
class Category(models.Model):
    categoryName = models.CharField(max_length=64, unique=True)  # наименование (уникальное)


# собственно новость|статья
class Post(models.Model):
    postAuthor = models.ForeignKey(Author, on_delete=models.CASCADE)
    postCategory = models.ManyToManyField(Category, through='LinkPostCategory')
    postRating = models.SmallIntegerField(default=0)
    postTitle = models.CharField(max_length=128)
    postCreated = models.DateTimeField(auto_now_add=True)

    news = 'N'
    article = 'A'
    POST_KIND = [
        (news, 'Новость'),
        (article, 'Статья')
    ]
    postKind = models.CharField(max_length=1, choices=POST_KIND, default=article)
    postBody = models.TextField(default='впишите текст новости|статьи')

    def __str__(self):
        return self.postTitle

    def like(self):
        self.postRating += 1
        self.save()

    def dislike(self):
        self.postRating -= 1
        self.save()

    def preview(self):
        return self.postBody[:124] + '...'


# таблица связи Post - many:many - Category
class LinkPostCategory(models.Model):
    linkedPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    linkedCategory = models.ForeignKey(Category, on_delete=models.CASCADE)


# Комментарий может создать не только Author, но и User; каждая сущности Post может иметь множество комментариев.
class Comment(models.Model):
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentCreated = models.DateTimeField(auto_now_add=True)
    commentBody = models.TextField(default='добавьте свой комментарий')
    commentRating = models.SmallIntegerField(default=0)

    # имя автора комментария: если не автор, то пользователь; упрощаем, получаем всегда пользователь
    def __str__(self):
        # try:
        #     return self.commentPost.postAuthor.authorUser.username
        # except:
        return self.commentUser.username

    def like(self):
        self.commentRating += 1
        self.save()

    def dislike(self):
        self.commentRating -= 1
        self.save()
