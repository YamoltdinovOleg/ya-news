# test_logic.py
from pytest_django.asserts import assertRedirects

from django.urls import reverse

from news.models import Comment

import pytest

# Дополнительно импортируем функцию slugify.
from pytils.translit import slugify

# Импортируем функции для проверки редиректа и ошибки формы:
from pytest_django.asserts import assertRedirects, assertFormError

# Импортируем из модуля forms сообщение об ошибке:
from news.forms import BAD_WORDS, WARNING

# Допишите импорт класса со статусами HTTP-ответов.
from http import HTTPStatus


# Анонимный пользователь не может отправить комментарий.
@pytest.mark.django_db
def test_anonymous_client_cant_send_note(client, form_data, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    # Через анонимный клиент пытаемся создать заметку:
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    # Проверяем, что произошла переадресация на страницу логина:
    assertRedirects(response, expected_url)
    # Считаем количество заметок в БД, ожидаем 0 заметок.
    assert Comment.objects.count() == 0


# Авторизованный пользователь может отправить комментарий.
@pytest.mark.django_db
def test_author_client_can_send_note(
    author_client, form_data, news_id_for_args
):
    url = reverse('news:detail', args=news_id_for_args)
    # Через автор клиент пытаемся создать заметку:
    author_client.post(url, data=form_data)

    # Считаем количество заметок в БД, ожидаем 1 заметок.
    assert Comment.objects.count() == 1


# Если комментарий содержит запрещённые слова, он не будет опубликован,
# а форма вернёт ошибку.
# Вызываем фикстуру отдельной заметки, чтобы в базе появилась запись.
@pytest.mark.django_db
def test_warning_words(author_client, news_id_for_args):
    # Подготавливаем данные с использованием плохих слов
    bad_word = BAD_WORDS[0]
    bad_words_data = {'text': f'Текст, {bad_word}, еще текст'}

    # Получаем URL для отправки комментария
    url = reverse('news:detail', args=news_id_for_args)

    # Отправляем POST-запрос с данными
    response = author_client.post(url, data=bad_words_data)

    # Проверяем наличие ошибки в форме
    assert 'form' in response.context
    form_errors = response.context['form'].errors['text']
    assert WARNING in form_errors

    # Проверяем, что комментарий не был создан
    assert Comment.objects.count() == 0


# Авторизованный пользователь может редактировать или удалять свои комментарии.
def test_author_client_can_edit_note(author_client, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    # Через автор клиент публик заметку:
    author_client.post(url, {'text': 'текст'})
    comment = Comment.objects.get()
    # Смотрим есть ли текст.
    assert comment.text == 'текст'


def test_author_client_can_delete_comment(author_client, news_id_for_args):
    url = reverse('news:delete', args=news_id_for_args)
    author_client.post(url)
    # Проверяем, что комментарий не был создан
    assert Comment.objects.count() == 0


# Авторизованный пользователь не может редактировать
# или удалять чужие комментарии.
def test_author_client_cant_edit_another_comment(
        author_client,
        another_comment_id_for_args
):
    url = reverse('news:edit', args=another_comment_id_for_args)
    # Через автор клиент публик заметку:
    author_client.post(url, {'text': 'текст'})
    comment = Comment.objects.get()
    # Смотрим есть ли текст.
    assert comment.text != 'текст'


def test_author_client_cant_delete_another_comment(
        author_client,
        another_comment_id_for_args
):
    url = reverse('news:delete', args=another_comment_id_for_args)
    # Отправляем POST-запрос с данными
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Проверяем, что комментарий было создано 1.
    assert Comment.objects.count() == 1












# # Указываем фикстуру form_data в параметрах теста.
# def test_user_can_create_note(author_client, author, form_data):
#     url = reverse('notes:add')
#     # В POST-запросе отправляем данные, полученные из фикстуры form_data:
#     response = author_client.post(url, data=form_data)
#     # Проверяем, что был выполнен редирект на страницу успешного добавления заметки:
#     assertRedirects(response, reverse('notes:success'))
#     # Считаем общее количество заметок в БД, ожидаем 1 заметку.
#     assert Note.objects.count() == 1
#     # Чтобы проверить значения полей заметки - 
#     # получаем её из базы при помощи метода get():
#     new_note = Note.objects.get()
#     # Сверяем атрибуты объекта с ожидаемыми.
#     assert new_note.title == form_data['title']
#     assert new_note.text == form_data['text']
#     assert new_note.slug == form_data['slug']
#     assert new_note.author == author
#     # Вроде бы здесь нарушен принцип "один тест - одна проверка";
#     # но если хоть одна из этих проверок провалится - 
#     # весь тест можно признать провалившимся, а последующие невыполненные проверки
#     # не внесли бы в отчёт о тесте ничего принципиально важного.



# # Следующий тест — проверка утверждения «анонимный пользователь не может создать заметку».
# # Добавляем маркер, который обеспечит доступ к базе данных:
# @pytest.mark.django_db
# def test_anonymous_user_cant_create_note(client, form_data):
#     url = reverse('notes:add')
#     # Через анонимный клиент пытаемся создать заметку:
#     response = client.post(url, data=form_data)
#     login_url = reverse('users:login')
#     expected_url = f'{login_url}?next={url}'
#     # Проверяем, что произошла переадресация на страницу логина:
#     assertRedirects(response, expected_url)
#     # Считаем количество заметок в БД, ожидаем 0 заметок.
#     assert Note.objects.count() == 0



# def test_empty_slug(author_client, form_data):
#     url = reverse('notes:add')
#     # Убираем поле slug из словаря:
#     form_data.pop('slug')
#     response = author_client.post(url, data=form_data)
#     # Проверяем, что даже без slug заметка была создана:
#     assertRedirects(response, reverse('notes:success'))
#     assert Note.objects.count() == 1
#     # Получаем созданную заметку из базы:
#     new_note = Note.objects.get()
#     # Формируем ожидаемый slug:
#     expected_slug = slugify(form_data['title'])
#     # Проверяем, что slug заметки соответствует ожидаемому:
#     assert new_note.slug == expected_slug


# # В параметрах вызвана фикстура note: значит, в БД создана заметка.
# def test_author_can_edit_note(author_client, form_data, note):
#     # Получаем адрес страницы редактирования заметки:
#     url = reverse('notes:edit', args=(note.slug,))
#     # В POST-запросе на адрес редактирования заметки
#     # отправляем form_data - новые значения для полей заметки:
#     response = author_client.post(url, form_data)
#     # Проверяем редирект:
#     assertRedirects(response, reverse('notes:success'))
#     # Обновляем объект заметки note: получаем обновлённые данные из БД:
#     note.refresh_from_db()
#     # Проверяем, что атрибуты заметки соответствуют обновлённым:
#     assert note.title == form_data['title']
#     assert note.text == form_data['text']
#     assert note.slug == form_data['slug']

# def test_other_user_cant_edit_note(not_author_client, form_data, note):
#     url = reverse('notes:edit', args=(note.slug,))
#     response = not_author_client.post(url, form_data)
#     # Проверяем, что страница не найдена:
#     assert response.status_code == HTTPStatus.NOT_FOUND
#     # Получаем новый объект запросом из БД.
#     note_from_db = Note.objects.get(id=note.id)
#     # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
#     assert note.title == note_from_db.title
#     assert note.text == note_from_db.text
#     assert note.slug == note_from_db.slug


# # Проверка удаления заметок
# def test_author_can_delete_note(author_client, slug_for_args):
#     url = reverse('notes:delete', args=slug_for_args)
#     response = author_client.post(url)
#     assertRedirects(response, reverse('notes:success'))
#     assert Note.objects.count() == 0


# def test_other_user_cant_delete_note(not_author_client, slug_for_args):
#     url = reverse('notes:delete', args=slug_for_args)
#     response = not_author_client.post(url)
#     assert response.status_code == HTTPStatus.NOT_FOUND
#     assert Note.objects.count() == 1 