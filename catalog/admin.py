from django.contrib import admin
from catalog.models import Author, Genre, Book, BookInstance, Profile, FavBooks

# Register your models here.


# admin.site.register(Book)
# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(BookInstance)


# Define the admin class
class BooksInline(admin.TabularInline):
    model = Book


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BooksInline]

# Fields are displayed vertically by default, but will display horizontally if you further group them in a tuple
# (as shown in the "date" fields above).


# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)


# we'll instead use the @register decorator to register the models
# (this does exactly the same thing as the admin.site.register() syntax)
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
# Register the Admin classes for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]

# display_genre is a function defined above and we'll define it below


# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )

    list_display = ('book', 'status', 'borrower', 'due_back', 'id')


admin.site.register(Profile)
admin.site.register(FavBooks)
