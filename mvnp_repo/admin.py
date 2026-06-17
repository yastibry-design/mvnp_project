from django.contrib import admin
from .models import Study, Category, Keyword


class KeywordInline(admin.TabularInline):
    model = Keyword
    extra = 2


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display  = ('study_id', 'title', 'authors', 'year',
                     'category', 'study_type', 'status', 'featured')
    list_filter   = ('study_type', 'status', 'featured', 'category')
    search_fields = ('title', 'authors', 'study_id', 'abstract')
    prepopulated_fields = {'study_id': ('title',)}
    inlines = [KeywordInline]
    fieldsets = (
        ('Identification', {
            'fields': ('study_id', 'title', 'authors', 'year')
        }),
        ('Classification', {
            'fields': ('category', 'study_type', 'status', 'featured')
        }),
        ('Content', {
            'fields': ('abstract', 'pdf_file')
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display       = ('name', 'order')
    list_editable      = ('order',)
    list_display_links = ('name',)
    ordering           = ('order', 'name')


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display  = ('word', 'study')
    list_filter   = ('study',)
    search_fields = ('word',)
