from django.test import TestCase
from django.urls import reverse
from catalog.models import Author
from django.contrib.auth.models import User  # Required to assign User as a borrower
from catalog.models import BookInstance, Book, Genre
import datetime
from django.utils import timezone
# import uuid
# from django.contrib.auth.models import Permission
# from django.contrib.auth.decorators import login_required
# from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from catalog.forms import EmailForm

# Create your tests here.


class IndexViewTest(TestCase):
    def setUp(self):

        test_user_1 = User.objects.create_superuser(username='testuser1',email='xyz@gmail.com', password='1X<ISRUkw+tuK')
        test_user_2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_staff=True)
        test_user_3 = User.objects.create_user(username='testuser3', password='2HJ1vRV0Z&3ik')

        test_user_1.save()
        test_user_2.save()
        test_user_3.save()

        # Create a book

        num_of_genre = 4

        for genre_id in range(num_of_genre):
            Genre.objects.create(name=f'genre {genre_id}')

        number_of_authors = 4

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f'firstname {author_id}',
                last_name=f'lastname {author_id}',
            )

        # test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        # test_language = Language.objects.create(name='English')

        for book_id in range(4):
            Book.objects.create(
                title=f'Book Title {book_id}',
                summary='My book summary',
                isbn='ABCDEFG',
                author=Author.objects.get(first_name=f'firstname {book_id}'),
            )

        # test_book = Book.objects.create(
        #     title='Book Title',
        #     summary='My book summary',
        #     isbn='ABCDEFG',
        #     author=test_author,
        #     # language=test_language,
        # )

        # Create genre as a post-step
        # genre_objects_for_book = Genre.objects.all()
        # test_book.genre.set(genre_objects_for_book)  # Direct assignment of many-to-many types not allowed.
        # test_book.save()

        # Create a BookInstance object for test_user
        # return_date = datetime.date.today() + datetime.timedelta(days=5)

        for i in range(4):
            BookInstance.objects.create(
                book=Book.objects.get(title=f'Book Title {i}'),
                imprint=f'Unlikely Imprint, 2016 {i}',
                due_back=datetime.date.today() + datetime.timedelta(days=i),
                borrower=test_user_1,
                status='o',
            )

        # # Create another BookInstance object for test_user
        # return_date = datetime.date.today() + datetime.timedelta(days=7)
        # self.test_bookinstance2 = BookInstance.objects.create(
        #     book=test_book,
        #     imprint='Unlikely Imprint, 2016',
        #     due_back=return_date,
        #     borrower=test_user,
        #     status='o',
        # )

    def test_count_of_entities(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        num_books = Book.objects.all().count()
        num_instances = BookInstance.objects.all().count()
        num_instances_available = BookInstance.objects.filter(status__exact='a').count()  # Available books(status='a')
        num_particular_books = Book.objects.filter(title__icontains='title')

        # The 'all()' is implied by default.
        num_authors = Author.objects.count()

        context = {
            'num_particular_books': num_particular_books,
            'num_books': num_books,
            'num_instances': num_instances,
            'num_instances_available': num_instances_available,
            'num_authors': num_authors,
        }

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)


class BookListViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

    @classmethod
    def setUpTestData(cls):
        number_of_books = 4

        for book_id in range(number_of_books):
            Book.objects.create(
                title=f'Book {book_id}',
                isbn=f'{book_id}',
                summary=f'{book_id} book created'
            )

        # return Book.objects.all()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('books'))
        # response = self.client.get(reverse('my-borrowed'))
        # self.assertEquals(response, '/accounts/login/?next=/catalog/books/')
        self.assertRedirects(response, '/accounts/login/?next=/catalog/books/')

    def test_lists_all_books(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('books') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['book_list']), 2)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('books'))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/book_list.html')

    def test_list_search_books(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        text = 'Book'
        response = self.client.get('/catalog/books/?search=Book')
        self.assertEqual(response.status_code, 200)


class AuthorListViewTest(TestCase):

    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        # test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        # test_user2.save()

    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_of_authors = 3

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f'Christian {author_id}',
                last_name=f'Surname {author_id}',
            )

    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get('/catalog/authors/')
        print("test_view_url_exists_at_desired_location, response = ", response)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('authors'))
        print("test_view_url_accessible_by_name, response=", response)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('authors'))
        # self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_two(self):
        login = self.client.login(
            username='testuser1',
            password='1X<ISRUkw+tuK'
        )
        response = self.client.get(reverse('authors'))
        # self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['author_list']) == 2)

    def test_lists_all_authors(self):
        login = self.client.login(
            username='testuser1',
            password='1X<ISRUkw+tuK'
        )
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('authors') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']) , 1)

    def test_list_search_authors(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        text = 'Christian'
        response = self.client.get('/catalog/authors/?search=Christian')
        self.assertEqual(response.status_code, 200)


class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(
            username='testuser1',
            password='1X<ISRUkw+tuK'
        )
        test_user2 = User.objects.create_user(
            username='testuser2',
            password='2HJ1vRV0Z&3iD'
        )

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(
            first_name='John',
            last_name='Smith'
        )
        test_genre = Genre.objects.create(name='Fantasy')
        # test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            # language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)  # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.now() + datetime.timedelta(days=book_copy % 5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(
            username='testuser1',
            password='1X<ISRUkw+tuK'
        )
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Now change all books to be on loan
        books = BookInstance.objects.all()[:10]

        for book in books:
            book.status = 'o'
            book.save()

        # Check that now we have borrowed books in the list
        response = self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)

        # Confirm all books belong to testuser1 and are on loan
        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status = 'o'
            book.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        # self.assertEqual(len(response.context['bookinstance_list']), 2)

        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back


# ----------------------------------------------------------------------------


class LoanedBookInstancesListViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(
            username='testuser1',
            password='1X<ISRUkw+tuK',
            is_staff=True,
        )
        test_user2 = User.objects.create_user(
            username='testuser2',
            password='2HJ1vRV0Z&3iD'
        )

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(
            first_name='John',
            last_name='Smith'
        )
        test_genre = Genre.objects.create(name='Fantasy')
        # test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            # language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)  # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.now() + datetime.timedelta(days=book_copy % 5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/borrowed/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_staff=True)
        response = self.client.get(reverse('borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(
            username='testuser1',
            password='1X<ISRUkw+tuK',
            is_staff=True
        )
        response = self.client.get(reverse('borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Now change all books to be on loan
        books = BookInstance.objects.all()[:10]

        for book in books:
            book.status = 'o'
            book.save()

        # Check that now we have borrowed books in the list
        response = self.client.get(reverse('borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)

        # Confirm all books belong to testuser1 and are on loan
        # for bookitem in response.context['bookinstance_list']:
        #     self.assertEqual(response.context['user'], bookitem.borrower)
        #     self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status = 'o'
            book.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK', is_staff=True)
        response = self.client.get(reverse('borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        # self.assertEqual(len(response.context['bookinstance_list']), 2)

        # last_date = 0
        # for book in response.context['bookinstance_list']:
        #     if last_date == 0:
        #         last_date = book.due_back
        #     else:
        #         self.assertTrue(BookInstance.is_overdue)
        #         last_date = book.due_back



# ----------------------------------------------------------------------------


class RenewBookInstancesViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_staff=True)

        test_user1.save()
        test_user2.save()

        # access = UserPassesTestMixin.get_test_func
        # print("access = ", access)

        # permission = Permission.objects.get(name='Set book as returned')
        # per = Permission.objects.get(user_set__is_staff=)
        # per = UserPassesTestMixin.get_test_func()
        # print("permission = ", permission)
        # test_user2.user_permissions.add(permission)
        # test_user2.save()

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
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user2,
            status='o',
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        # self.assertTrue(response.url.startswith('/accounts/login/'))

    # def test_redirect_if_logged_in_but_not_correct_permission(self):
    #     login = self.client.login(
    #         username='testuser1',
    #         password='1X<ISRUkw+tuK'
    #     )
    #     response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
    #     self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance2.pk}))

        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))

        # Check that it lets us login. We're a librarian, so we can view any users book
        self.assertEqual(response.status_code, 200)

    # def test_HTTP404_for_invalid_book_if_logged_in(self):
    #     # unlikely UID to match our bookinstance!
    #     test_uid = uuid.uuid4()
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
    #     response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': test_uid}))
    #     self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)
        response_for_valid = self.client.get(reverse('borrowed'))
        self.assertTemplateUsed((response_for_valid, 'catalog/bookinstance_list_borrowed.html'))

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    def test_redirect_when_renew_done(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        valid_date_in_future = datetime.date.today()
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                    {'due_back': valid_date_in_future}, is_valid=True)
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        valid_response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                          {'renewal_date': valid_date_in_future})
        self.assertRedirects(valid_response, reverse('borrowed'))
        # print(response.context)
        # print("---------------------\n",response)
        # self.assertEqual(response.due_back, reverse('borrowed'))


class AuthorCreateTest(TestCase, UserPassesTestMixin):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        self.test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_superuser=True)

        test_user1.save()
        # test_user2.save()

    def test_not_logged_in_302(self):
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_not_have_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_as_staff_enter(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')

    def test_func(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(self.test_user2.is_superuser, True)


class AuthorDetailTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_superuser=True)

        test_user1.save()
        test_user2.save()

        self.test_author = Author.objects.create(
            first_name='John',
            last_name='Smith',
        )

        # test_author.save()

    def test_not_logged_in_302(self):
        response = self.client.get(reverse('author-detail', kwargs={'pk': self.test_author.pk}))
        self.assertEqual(response.status_code, 302)

    # def test_logged_in_not_have_permission(self):
    #     login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
    #     response = self.client.get(reverse('author-detail', kwargs={'pk': self.test_author.pk}))
    #     self.assertEqual(response.status_code, 403)

    def test_logged_in_as_staff_enter(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author-detail' , kwargs={'pk': self.test_author.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_detail.html')


class AuthorUpdateTest(TestCase, UserPassesTestMixin):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        self.test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_superuser=True)

        self.test_author = Author.objects.create(
            first_name='John',
            last_name='Smith',
        )

    def test_func(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author_update', kwargs={'pk': self.test_author.pk}))
        self.assertEqual(self.test_user2.is_superuser, True)


class AuthorDeleteTest(TestCase, UserPassesTestMixin):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        self.test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_superuser=True)

        self.test_author = Author.objects.create(
            first_name='John',
            last_name='Smith',
        )

    def test_func(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author_delete', kwargs={'pk': self.test_author.pk}))
        self.assertEqual(self.test_user2.is_superuser, True)


class BookCreateTest(TestCase, UserPassesTestMixin):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        self.test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_superuser=True)

        test_user1.save()
        # test_user2.save()

    def test_not_logged_in_302(self):
        response = self.client.get(reverse('book_create'))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_not_have_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('book_create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_as_staff_enter(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_form.html')

    def test_func(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book_create'))
        self.assertEqual(self.test_user2.is_superuser, True)


class BookUpdateTest(TestCase, UserPassesTestMixin):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        self.test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_superuser=True)

        test_author = Author.objects.create(
            first_name='John',
            last_name='Smith',
        )

        # test_genre = Genre.objects.create(
        #     name='Genre1',
        # )

        self.test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            # language=test_language,
            # genre=test_genre.objects.get(name='Genre1'),
        )

        test_genre = Genre.objects.create(name='Fantasy')
        genre_objects_for_book = Genre.objects.all()
        self.test_book.genre.set(genre_objects_for_book)

        # self.test_book.genre.set(self.test_genre)

    def test_func(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book_update', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(self.test_user2.is_superuser, True)

    def test_the_template_used(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book_update', kwargs={'pk': self.test_book.pk}))
        self.assertTemplateUsed(response, 'catalog/book_form.html')


class BookDeleteTest(TestCase, UserPassesTestMixin):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        self.test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_superuser=True)

        test_author = Author.objects.create(
            first_name='John',
            last_name='Smith',
        )

        self.test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            # language=test_language,
            # genre=test_genre.objects.get(name='Genre1'),
        )

        test_genre = Genre.objects.create(name='Fantasy')
        genre_objects_for_book = Genre.objects.all()
        self.test_book.genre.set(genre_objects_for_book)

    def test_func(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book_delete', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(self.test_user2.is_superuser, True)


class EmailViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        self.test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_superuser=True)

        test_author = Author.objects.create(
            first_name='John',
            last_name='Smith',
        )

        self.test_book = Book.objects.create(
            title='Book 3',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            # language=test_language,
            # genre=test_genre.objects.get(name='Genre1'),
        )

        test_genre = Genre.objects.create(name='Fantasy')
        genre_objects_for_book = Genre.objects.all()
        self.test_book.genre.set(genre_objects_for_book)

        form = EmailForm()

    def test_login_compulsory(self):
        response = self.client.get(reverse('email', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(response.status_code, 302)

    def test_template_used(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('email', kwargs={'pk': self.test_book.pk}))
        # self.assertEqual('catalog/email_form.html' in response, True)
        self.assertTemplateUsed(response, 'catalog/email_form.html')

    def test_Send_Email(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('email', kwargs={'pk': self.test_book.pk}),
                                    {'email_id': 'kediavedansh@gmail.com'})
        self.assertRedirects(response, reverse('my-borrowed'))
