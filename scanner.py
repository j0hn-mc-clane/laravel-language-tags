import os
import re

class Scanner:
    project_path = ''
    scanner_path = ''
    export_type = ''
    languages = ['en', 'nl', 'fr', 'de']
    language_tags = {}

    def __init__(self):
        self.setup_project_path()
        self.get_languages()
        self.check_export_format()
        self.scanner_path = self.project_path + '/resources/views'
        print('Scanning files for @lang tags ...')
        self.scan_files(self.scanner_path)
        print('Exporting ...')
        self.export_tags_to_file()

    '''
        Sets project path and removes trailing slash
    '''
    def setup_project_path(self):
        project_path = raw_input('Give the full path to the project folder: \n')
        if self.check_if_dir_exists(project_path):
            if project_path.endswith('/'):
                project_path = project_path[:-1]
            self.project_path = project_path
        else:
            self.setup_project_path()

    '''
        Prompts user to input a comma-separated list of languages needed
        Use default if user provides none
    '''
    def get_languages(self):
        langs = raw_input('For what language codes do you want to generate files? Default: en, nl, de, fr. Split using comma: \n')
        try:
            arr = langs.split(',')
            if arr[0] is not None:
                self.languages = arr
        except Exception:
            print('Error. Try again.')
            self.get_languages()

    '''
        Set export format to PHP or JSON
    '''
    def check_export_format(self):
        export_choice = raw_input('Export as php or json?\n')

        if export_choice == 'php':
            self.export_type = 'php'

        elif export_choice == 'json':
            self.export_type = 'json'

        else:
            print('Wrong format, be sure to type php or json')
            self.check_export_format()

    '''
        Scans all files in the dir
        Recursively walk through subdirs
    '''
    def scan_files(self, dir_path):
        for (path, dirs, files) in os.walk(dir_path):
            for d in dirs:
                self.scan_files(d)

            for f in files:
                if f.endswith('.php'):
                    self.retrieve_tags_from_file(f, path)

    '''
        Fetches all language tags from a file and 
        insert them at respective file key in global dictionary
    '''
    def retrieve_tags_from_file(self, filename, dir_path):
        with open(dir_path + '/' + filename)as f:
            contents = f.readlines()
            for line in contents:
                # Regex
                lang = re.findall(r'(@lang)(.*)\)', line)
                if len(lang) > 0:
                    lang_line = lang[0][1].replace('(', '')
                    lang_line = lang_line.replace('\'', '')
                    lang_array = lang_line.split('.')

                    # Already in dictionary, append to the list
                    if self.language_tags.get(lang_array[0]) is not None:
                        val = self.language_tags[lang_array[0]]
                        arr = list(val)
                        arr.append(lang_array[1])
                        self.language_tags[lang_array[0]] = arr

                    # Create new list at key
                    else:
                        self.language_tags[lang_array[0]] = [lang_array[1]]

    '''
        Exports language tags to respective files in respective lang folders
    '''
    def export_tags_to_file(self):
        # Loop over languages
        for language in self.languages:
            # Set dir_path for each language
            dir_path = '/Users/diff/test-laravel-scan/' + language
            print('Create files in: ' + dir_path + ' ...')

            # Loop over dictionary
            for key, val in self.language_tags.items():

                # If the language folder does not exist, create it
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                # Open the file represented by the lang key,
                # e.g. @lang('backend.portfolio') where backend is key
                with open(dir_path + '/' + key + '.' + self.export_type, 'a+') as file:
                    print('Creating file: ' + file.name + ' ...')

                    # Write PHP file declarations
                    if self.export_type is 'php':
                        file.write('<?php')
                        file.write('\n')
                        file.write('return [')

                    # Loop over values and insert the language tags
                    for v in val:
                        file.write('\n')
                        file.write('\'' + v + '\'' + ' => \'\',')
                    file.write('];')

    '''
        Checks if dir exists
    '''
    def check_if_dir_exists(self, dir):
        return os.path.exists(dir)
