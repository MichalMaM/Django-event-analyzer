from django.contrib import admin

from eventanalyzer.models import Report, ReportResult

#class ReportArchiveInline(admin.StackedInline):
#    model = ReportArchive
#    list_editable = ('output',)
#    extra = 5

class ReportAdmin(admin.ModelAdmin):
#    fieldsets = [
#        (None,               {'fields': ['title']}),
#	(None,               {'fields': ['description']}),
#	(None,               {'fields': ['db_query']}),
#	(None,               {'fields': ['interval']}),
        #('Date of last report ', {'fields': ['last_report'], 'classes': ['collapse']}),
#    ]
    #inlines = [ReportArchiveInline]

    list_display = ('title', 'description', 'interval', 'last_report')
    search_fields = ['title']
    date_hierarchy = 'last_report'

class ReportResultAdmin(admin.ModelAdmin):

    list_display = ('report', 'run_date')
    search_fields = ['report']
    list_filter = ['report']
    date_hierarchy = 'run_date'
    
    

admin.site.register(Report, ReportAdmin)
admin.site.register(ReportResult, ReportResultAdmin)