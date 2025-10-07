# Installation packages in general mode (from gz file)

- The --user flag installs packages to your user's site-packages directory (outside the virtual environment)

    ``` python -m pip install --user django-polls/dist/django_polls-0.1.tar.gz ```

- When you're in a virtual environment, don't use --user flag.

    ``` python -m pip install django-polls/dist/django_polls-0.1.tar.gz ```

# Installation packages in developement mode (from package source folder)

Generally, you need to rebuild and reinstall the package if you've made changes to the code.

- To reflect your changes on the server, you need to rebuild and reinstall the package.

    ``` pip install --upgrade django-polls/dist/django_polls-0.1.tar.gz ```

## **Better approach for development:**

Instead of rebuilding/reinstalling every time, install the package in editable mode (development mode):

```pip install -e django-polls/```

To verify it's installed in editable mode:

- ```pip list```
    - Look for your package name with a path showing it's editable (usually shows the source directory path).
- ```pip show django-polls```
    - It will show Location: pointing to your source directory and Editable project location: with the path.
