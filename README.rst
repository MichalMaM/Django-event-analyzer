====================
Django event analyzer
====================

Django-event-analyzer is a simple application where you can create periodic reports by mongo query that is set in django admin.
This reports are using as data source for analysis that you can also set in django admin for priodic repetition.

Installation
============

 * create your django project 
 * add ``eventanalyzer`` to your ``INSTALLED_APPS`` and ``eventanalyzer.urls``
   somewhere in your URLs
 * customize your settings, see ``eventanalyzer.conf`` for complete list of
   options and their default values

Use
===

Set your query (and other parametrs) for periodic reports in django admin.
Set your analysis for periodic repetition in django admin
Add jobs.py from eventanalyzer to yout crontable.

