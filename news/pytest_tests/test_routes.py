# test_routes.py
import pytest  # Импортируем pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects


# Главная страница доступна анонимному пользователю.
# Указываем в фикстурах встроенный клиент.
@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
# Указываем имя изменяемого параметра в сигнатуре теста.
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


# Cтраница отдельной новости доступна анонимному пользователю.
@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('news:detail',)
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_detail_for_anonymous_user(not_author_client, name, news):
    url = reverse(name, args=(news.id,))  # Получаем ссылку на нужный адрес.
    response = not_author_client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


# Страницы удаления и редактирования комментария доступны автору комментария.
@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('news:delete', 'news:edit')
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_delete_edit_for_comment_author(author_client, name, comment):
    url = reverse(name, args=(comment.id,))  # Получаем ссылку на нужный адрес.
    response = author_client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


# При попытке перейти на страницу редактирования или
# удаления комментария анонимный пользователь
# перенаправляется на страницу авторизации.
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_for_args')),
    ),
)
# Передаём в тест анонимный клиент, name проверяемых страниц и args:
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    # Теперь не надо писать никаких if и можно обойтись одним выражением.
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


# Авторизованный пользователь не может зайти на страницы
# редактирования или удаления чужих комментариев (возвращается ошибка 404).
@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('news:delete', 'news:edit')
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_delete_edit_for_another_author(
    author_client,
    name,
    another_comment
):
    url = reverse(name, args=(another_comment.id,))  # Получаем ссылку
    response = author_client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.NOT_FOUND


# Страницы регистрации пользователей, входа в учётную запись
# и выхода из неё доступны анонимным пользователям.
@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    ('users:signup', 'users:login', 'users:logout')
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_auth_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK
