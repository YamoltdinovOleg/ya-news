# conftest.py
import pytest

from datetime import datetime, timedelta
from django.utils import timezone

# Импортируем класс клиента.
from django.test.client import Client

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import News, Comment


DAYS_OF_NEWS = 10


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):  
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news(author):
    news = News.objects.create(  # Создаём объект заметки.
        title='Заголовок',
        text='Текст заметки',
        # slug='note-slug',
        # author=author,
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(  # Создаём объект заметки.
        # title='Заголовок',
        text='Текст заметки',
        # slug='note-slug',
        author=author,
        news_id=news.id
    )
    return comment


@pytest.fixture
# Фикстура запрашивает другую фикстуру создания заметки.
def comment_for_args(comment):
    # И возвращает кортеж, который содержит slug заметки.
    # На то, что это кортеж, указывает запятая в конце выражения.
    return (comment.id,)


@pytest.fixture
def another_comment(not_author, news):
    another_comment = Comment.objects.create(
        news_id=news.id,
        text='Текст заметки',
        author=not_author,
    )
    return another_comment


@pytest.fixture
def news_pages(author):
    news_pages = []
    today = datetime.today()
    for i in range(DAYS_OF_NEWS):
        news_pages.append(
            News.objects.create(
                title='Заголовок',
                text='Текст заметки',
                date=today - timedelta(days=i)
            )
        )
    return news_pages


@pytest.fixture
def comment_list(author, news):
    now = timezone.now()
    comments = [
        Comment(
            news_id=news.id,
            text='Текст заметки',
            author=author,
            created=now + timedelta(days=i)
        ) for i in range(3)
    ]
    Comment.objects.bulk_create(comments)
    return comments


@pytest.fixture
def news_id_for_args(news):
    return (news.id,)


# Добавляем фикстуру form_data
@pytest.fixture
def form_data():
    return {
        # 'title': 'Новый заголовок',
        'text': 'Новый текст',
        # 'slug': 'new-slug'
    }


@pytest.fixture
def another_comment_id_for_args(another_comment):
    return (another_comment.id,)