from django.contrib import admin
from eventanalyzer.models import Report, ReportResult, Analysis, AnalysisResult
from eventanalyzer.forms import ReportAdminForm

class ReportAdmin(admin.ModelAdmin):
    form = ReportAdminForm

    list_display = ('title', 'description', 'interval', 'last_report')
    search_fields = ['title']
    date_hierarchy = 'last_report'

class ReportResultAdmin(admin.ModelAdmin):

    list_display = ('report', 'run_date', 'output')
    search_fields = ['report']
    list_filter = ['report']
    date_hierarchy = 'run_date'

class AnalysisAdmin(admin.ModelAdmin):

    list_display = ('title', 'description', 'interval', 'last_report')
    search_fields = ['title']
    date_hierarchy = 'last_report'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'plug_in', 'interval', 'queries', 'activated')
        }),
        ('Queries options', {
            'classes': ('collapse',),
            'fields': ('date_from', 'date_to')
        }),
	('Date of last executed analysis', {
            'fields': ('last_report',)
        }),
    )

class AnalysisResultAdmin(admin.ModelAdmin):

    list_display = ('analysis', 'run_date', 'output')
    search_fields = ['analysis']
    list_filter = ['analysis']
    date_hierarchy = 'run_date'
    

admin.site.register(Report, ReportAdmin)
admin.site.register(ReportResult, ReportResultAdmin)
admin.site.register(Analysis, AnalysisAdmin)
admin.site.register(AnalysisResult, AnalysisResultAdmin)