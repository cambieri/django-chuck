#!/bin/bash

# run unit tests
python django_chuck/test.py || exit 1
python django_chuck/commands/test.py  || exit 1
python django_chuck/template/notch_interactive/test.py || exit 1


# test commands
chuck list_modules || exit 1
chuck search_module cms || exit 1
chuck show_info fabric || exit 1
chuck create_project test test || exit 1
chuck create_project test test django-cms south uwsgi nginx || exit 1

exit 0