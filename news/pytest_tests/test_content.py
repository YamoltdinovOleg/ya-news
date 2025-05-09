# test_content.py
import pytest
from django.urls import reverse
from news.pytest_tests.conftest import DAYS_OF_NEWS
from news.forms import CommentForm


# Количество новостей на главной странице — не более 10
# В тесте используем фикстуру заметки
# и фикстуру клиента с автором заметки.
def test_pages_in_list_for_author(news_pages, author_client):
    url = reverse('news:home')
    # Запрашиваем страницу со списком заметок:
    response = author_client.get(url)
    # Получаем список объектов из контекста:
    object_list = response.context['object_list']
    # Проверяем, что заметка находится в этом списке:
    assert object_list.count() <= DAYS_OF_NEWS


# Новости отсортированы от самой свежей к самой старой.
# Свежие новости в начале списка.
# test_content.py
@pytest.mark.parametrize(
    # Задаём названия для параметров:
    'parametrized_client, news_in_list',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (pytest.lazy_fixture('author_client'), None),
    )
)
def test_news_sort(
        # Используем фикстуру заметки и параметры из декоратора:
        news_pages, parametrized_client, news_in_list
):
    url = reverse('news:home')
    # Выполняем запрос от имени параметризованного клиента:
    response = parametrized_client.get(url)
    object_list = response.context['object_list']

    # Извлекаем даты и сортируем их
    all_dates = list(map(lambda news: news.date, object_list))
    assert all_dates == sorted(all_dates, reverse=True)

# Комментарии на странице отдельной новости отсортированы в
# хронологическом порядке: старые в начале списка, новые — в конце.
@pytest.mark.parametrize(
    # Задаём названия для параметров:
    'parametrized_client, news_in_list',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (pytest.lazy_fixture('author_client'), None),
    )
)
def test_news_comment(
        # Используем фикстуру заметки и параметры из декоратора:
        news, comment_list, parametrized_client, news_in_list, news_id_for_args
):
    url = reverse('news:detail', args=(news_id_for_args))
    # Выполняем запрос от имени параметризованного клиента:
    response = parametrized_client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()

    # Получаем временные метки создания комментариев
    all_timestamps = [comment.created for comment in all_comments]

    # Проверяем, что список временных меток не пустой
    if all_timestamps:
        sorted_timestamps = sorted(all_timestamps)
        assert all_timestamps == sorted_timestamps
    else:
        # Если комментариев нет, можно просто проверить, что список пустой
        assert not all_comments.exists()

# Анонимному пользователю недоступна форма для отправки комментария
# на странице отдельной новости, а авторизованному доступна.
@pytest.mark.parametrize(
    # Задаём названия для параметров:
    'parametrized_client, response',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (pytest.lazy_fixture('not_author_client'), True),
    )
)
def test_news_form_not_author(
        # Используем фикстуру заметки и параметры из декоратора:
        parametrized_client, response, news_id_for_args
):
    url = reverse('news:detail', args=news_id_for_args)
    # Выполняем запрос от имени параметризованного клиента:
    response = parametrized_client.get(url)

    # Извлекаем даты и сортируем их
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.parametrize(
    # Задаём названия для параметров:
    'parametrized_client, response',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (pytest.lazy_fixture('client'), False),
    )
)
def test_news_form_not_client(
        # Используем фикстуру заметки и параметры из декоратора:
        parametrized_client, response, news_id_for_args
):
    url = reverse('news:detail', args=news_id_for_args)
    # Выполняем запрос от имени параметризованного клиента:
    response = parametrized_client.get(url)

    # Извлекаем даты и сортируем их
    assert 'form' not in response.context
