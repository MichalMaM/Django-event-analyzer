from django.contrib import admin
from eventanalyzer.models import Report, ReportResult

class ReportAdmin(admin.ModelAdmin):

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