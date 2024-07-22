# news/tests/test_logic.py
from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    comments_count_first = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    comments_count_second = Comment.objects.count()
    assert comments_count_second == comments_count_first

@pytest.mark.parametrize(
   'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('client'), True),
        (pytest.lazy_fixture('author_client'), False)
    ),
)
def test_users_create_comment(parametrized_client,
                              news,
                              form_data,
                              expected_status):
    comments_count_first = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    parametrized_client.post(url, data=form_data)
    comments_count_second = Comment.objects.count()
    assert ((comments_count_first == comments_count_second) == expected_status)


def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
        )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, comment, news):
    comments_count_first = Comment.objects.count()
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url)
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    assertRedirects(response, url_to_comments)
    comments_count_second = Comment.objects.count()
    assert comments_count_first != comments_count_second


def test_user_cant_delete_comment(not_author_client, comment):
    comments_count_first = Comment.objects.count()
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_second = Comment.objects.count()
    assert comments_count_first == comments_count_second


def test_author_can_edit_comment(author_client, form_data, comment, news):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data=form_data)
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment(not_author_client, form_data, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == "Текст комментария"
