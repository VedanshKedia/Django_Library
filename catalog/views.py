from django.shortcuts import render, get_object_or_404
from catalog.models import Book, Author, BookInstance, Profile, FavBooks
from django.views import generic
from django.views.generic import View
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth import login, authenticate
from catalog.forms import RenewBookForm, EmailForm, SearchForm, ProfileForm
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.db.models import Q
from django.shortcuts import render, HttpResponseRedirect, reverse, redirect
from django.contrib.auth.models import User
from functools import reduce
import operator
import json
# from django.http import HttpResponse
# from django.http import request
# Create your views here.


# def signup(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             raw_password = form.cleaned_data.get('password1')
#             user = authenticate(username=username, password=raw_password)
#             login(request, user)
#             return redirect('index')
#     else:
#         form = UserCreationForm()
#     return render(request, 'signup.html', {'form', form})

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


# try to make this a class-based view and include mixin for authentication
@login_required
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_particular_books = Book.objects.filter(title__icontains='Assignment')

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    context = {
        'num_particular_books': num_particular_books,
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    paginate_by = 2

    def get_queryset(self):
        object_list = super(BookListView, self).get_queryset()
        print("object_list = ", object_list)
        # print("image location = ", Book.image.url)
        text = self.request.GET.get('search')
        if text:
            # print("filtered = ", Book.objects.filter(title__icontains=text))
            object_list = object_list.filter(title__icontains=text)
            # print("text=", text)
            # print("Edited object list = ", object_list)

        return object_list


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book


class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Author
    paginate_by = 2

    def get_queryset(self):
        object_list = super(AuthorListView, self).get_queryset()
        print("object_list = ", object_list)
        text = self.request.GET.get('search')
        if text:
            # print("filtered = ", Author.objects.filter(Q(first_name__icontains=text) | Q(last_name__icontains=text)))
            object_list = object_list.filter(Q(first_name__icontains=text) | Q(last_name__icontains=text))
            # print("text=", text)
            # print("Edited object list = ", object_list)
        return object_list


class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed.html'
    paginate_by = 10
    # permission_required = 'can_mark_returned'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o')


# @permission_required('catalog.can_mark_returned')
@staff_member_required
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}

    def test_func(self):
        return self.request.user.is_superuser


class AuthorUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

    def test_func(self):
        return self.request.user.is_superuser


class AuthorDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

    def test_func(self):
        return self.request.user.is_superuser


class BookCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Book
    fields = '__all__'
    # initial = {'date_of_death': '05/01/2018'}

    def test_func(self):
        return self.request.user.is_superuser


class BookUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']

    def test_func(self):
        return self.request.user.is_superuser


class BookDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')

    def test_func(self):
        return self.request.user.is_superuser


@login_required
def emailview(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = EmailForm(request.POST)
        email_id = []
        if form.is_valid():
            email_id.append(form.cleaned_data['email_id'])
            email = EmailMessage(
                book.title,
                'Enjoy Reading',
                'vedansh.kedia.iitb@gmail.com',
                email_id,
            )
            email.attach_file('catalog/docs/'+book.title+'.pdf')
            email.send()
            return HttpResponseRedirect(reverse('my-borrowed'))
    else:
        form = EmailForm()
        return render(request, 'catalog/email_form.html', {'form': form})


# @login_required
# def profile_form(request):
#     if request.method == 'POST':
#         form = ProfileForm(request.POST)
#
#         # if form.is_valid():
#


class ProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'catalog/profile.html'
    form_class = ProfileForm
    success_url = '/catalog/'
    # fields = ['image', 'number', 'fav_book',]

    # user_instance = Profile.objects.filter(user=req)

    # def get(self, request, *args, **kwargs):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.all()
        return context

    # def get(self, request, *args, **kwargs):
    #     if Profile.objects.get(user=request.user):

    def post(self, request, *args, **kwargs):
        # fav_book_list = []
        form = ProfileForm(request.POST, request.FILES)

        if form.is_valid():
            image = form.cleaned_data["image"]
            number = form.cleaned_data["number"]
            fav_book_list = request.POST.get("fav_book_list")
            fav_book_list = json.loads(fav_book_list)
            for fav_book in fav_book_list:
                print(fav_book)
                print("\n",FavBooks.objects.filter(fav_book=fav_book))
                print("\n",bool(FavBooks.objects.filter(fav_book=fav_book)))
                if bool(FavBooks.objects.filter(fav_book=fav_book)):
                    pass
                else:
                    FavBooks.objects.create(fav_book=fav_book)

            fav_book_object = FavBooks.objects.filter(fav_book__in=fav_book_list)

            print("--------------------------------------------\n")
            print(fav_book_object)
            print("--------------------------------------------\n")

            profile_object = Profile.objects.get(user=request.user)

            profile_object.image = image
            profile_object.number = number

            profile_object.fav_book.set(fav_book_object)

            profile_object.save()


            # profile_data = Profile.objects.filter(user=request.user).update(
            #     image=image,
            #     number=number,
            #     fav_book=fav_book_object,
            # )

            # profile_data.fav_book.set(fav_books_)

        return HttpResponseRedirect(reverse('my-borrowed'))

        # return super().form_valid(form)
    # def form_valid(self, form):

        # form.instance.created_by = self.request.user


    # def get(self, request, *args, **kwargs):
    #     if Profile.objects.get(user=request.user):
    #         return render(request, self.template_name, context={''})


    # ------------------------------------------------------------------------

    # def post(self, request, *args, **kwargs):
    #     form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
    #     print(Profile.objects.get(user=request.user))
    #     if Profile.objects.get(user=request.user):
    #         if form.is_valid():
    #             image = form.cleaned_data['image']
    #             number = form.cleaned_data['number']
    #             print("\n\n-----------------\n\n", form.cleaned_data['fav_book'])
    #             # fav_book = FavBooks.objects.filter(fav_book__icontains=form.cleaned_data['fav_book'])
    #             # print("\n\n-----------------\n\n", fav_book)
    #             fav_book = form.cleaned_data['fav_book']
    #             fav_books = FavBooks.objects.filter(fav_book__in=fav_book)
    #             profile_data = Profile.objects.create(
    #                 user=request.user,
    #                 image=image,
    #                 number=number,
    #                 # fav_book=fav_book,
    #             )
    #             profile_data.fav_book.set(fav_books)
    #             profile_data.save()
    #             return HttpResponseRedirect(reverse('my-borrowed'))
    #         else:
    #             return render(request, 'catalog/profile.html', {'form_errors': form.errors, 'form': form})
    #
    #     else:
    #         if form.is_valid():
    #
    #             image = form.cleaned_data['image']
    #             number = form.cleaned_data['number']
    #             print("\n\n-----------------\n\n", form.cleaned_data['fav_book'])
    #             # fav_book = FavBooks.objects.filter(fav_book__icontains=form.cleaned_data['fav_book'])
    #             # print("\n\n-----------------\n\n", fav_book)
    #             fav_book = form.cleaned_data['fav_book']
    #             profile_data = Profile.objects.create(
    #                 # user=User.objects.get(pk=request.user_id),
    #                 user=request.user,
    #                 image=image,
    #                 number=number,
    #                 fav_book=fav_book,
    #             )
    #
    #             profile_data.save()
    #             return HttpResponseRedirect(reverse('my-borrowed'))
    #         else:
    #             return render(request, 'catalog/profile.html', {'form_errors': form.errors, 'form':form})
    #
    # def get(self, request, *args, **kwargs):
    #     # form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
    #     #
    #     # if form.is_valid():
    #     #     form.save()
    #     form = ProfileForm()
    #     return render(request, 'catalog/profile.html', {'form': form,
    #                                                     'book': Book.objects.all(),
    #                                                     'Profile': Profile.objects.filter(user=request.user)})
    #


    # ------------------------------------------------------------------------------------





    # def form_valid(self, form):
    #     us



# ---------------------------------Commented Code---------------------------------------------------

#
# class BookSearchListView(BookListView):
#     def get_queryset(self):
#         result = super(BookSearchListView, self).get_queryset()
#
#         query = self.request.GET.get('q')
#         if query:
#             query_list = query.split()
#             result = result.filter(
#                 reduce(operator.and_,
#                        (Q(title__icontains=q) for q in query_list))
#             )
#             print(result)
#         return result

    # form = SearchForm

    # def get_queryset(self):
    #
    #     res = super(BookListView, self).get_queryset()
    #     text = self.request.GET.get('search')
    #     if text:
    #         text_list = text.split()
    #         res = res.filter(reduce(operator.and_,
    #                                          Q(title__icontains=text) for text in text_list))

        # return res
        # form = self.form(self.request.GET)
        # if form.is_valid():
        #     return Book.objects.filter(title__icontains=self.kwargs['search'])
        # return Book.objects.all()
        # try:
        #     name = self.kwargs['search']
        # except:
        #     name = ''
        # if name != '':
        #     object_list = self.model.objects.filter(title__icontains=name)
        # else:
        #     object_list = self.model.objects.all()
        # return object_list

# def searchform(request):
#     if request.method == 'POST':
#         form = SearchBookForm(request.POST)
#         if form.is_valid():
#             return HttpResponseRedirect(reverse('books'))
#         else:
#             return HttpResponseRedirect(reverse('books'))
#

# def emailview(request, pk):
#     book = get_object_or_404(Book, pk=pk)
#     if request.method == 'POST':
#         form = EmailForm(request.POST)
#         email_id = []
#         if form.is_valid():
#             email_id.append(form.cleaned_data['email_id'])
#             email = EmailMessage(
#                 book.title,
#                 'Enjoy Reading',
#                 'vedansh.kedia.iitb@gmail.com',
#                 email_id,
#             )
#             email.attach_file('catalog/docs/'+book.title+'.pdf')
#             email.send()
#             return HttpResponseRedirect(reverse('my-borrowed'))
#     else:
#         form = EmailForm()
#         return render(request, 'catalog/email_form.html', {'form': form})
