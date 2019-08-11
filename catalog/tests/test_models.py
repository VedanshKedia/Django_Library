from django.test import TestCase
from catalog.models import Author, BookInstance, Book, Genre, Language
from django.contrib.auth.models import User
import datetime
from datetime import date
from django.utils import timezone
# Create your tests here.


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, 'first name')

    def test_date_of_death_label(self):
        author=Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEquals(field_label, 'died')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = f'{author.last_name}, {author.first_name}'
        self.assertEquals(expected_object_name, str(author))

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEquals(author.get_absolute_url(), f'/catalog/author/{author.id}')


class BookTest(TestCase):
    def setUp(self):
        test_author = Author.objects.create(
            first_name='John',
            last_name='Smith'
        )

        # test_language = Language.objects.create(name='English')
        self.test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            # language=test_language,
        )

        # Create genre as a post-step
        test_genre = Genre.objects.create(name='Fantasy')
        genre_objects_for_book = Genre.objects.all()
        self.test_book.genre.set(genre_objects_for_book)  # Direct assignment of many-to-many types not allowed.
        # test_book.save()

    def test_str(self):
        self.assertEqual(self.test_book.__str__(), 'Book Title')

    def test_get_absolute_url(self):
        self.assertEquals(self.test_book.get_absolute_url(), f'/catalog/book/{self.test_book.id}')


class LanguageTest(TestCase):
    def setUp(self):
        self.language = Language.objects.create(name='English')

    def test_string_returned_at_admin_panel(self):
        self.assertEqual(self.language.__str__(),
                         'English')


class GenreTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name='fiction')

    def test_string_returned_at_admin_panel(self):
        self.assertEqual(self.genre.__str__(),
                         'fiction')


class BookInstanceTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_staff=True)

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(
            first_name='John',
            last_name='Smith'
        )

        # test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            # language=test_language,
        )

        # Create genre as a post-step
        test_genre = Genre.objects.create(name='Fantasy')
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)  # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user1,
            status='o',
        )

        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=-5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user2,
            status='o',
        )

    def test_string_returned_at_admin_panel(self):
        self.assertEqual(self.test_bookinstance1.__str__(),
                         f'{self.test_bookinstance1.id} ({self.test_bookinstance1.book.title})')

    def test_is_overdue(self):
        last_date = 0
        # for book in response.context['bookinstance_list']:
        if self.test_bookinstance1.due_back < date.today():
            self.assertEqual(self.test_bookinstance1.is_overdue, True)
        else:
            self.assertEqual(self.test_bookinstance1.is_overdue, False)
        # else:
            # self.assert
            # last_date = book.due_back
        if self.test_bookinstance2.due_back < date.today():
            self.assertEqual(self.test_bookinstance2.is_overdue, True)
        else:
            self.assertEqual(self.test_bookinstance2.is_overdue, False)