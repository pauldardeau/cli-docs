# generate man page source from .ini file

# helpful links:
#   http://liw.fi/manpages/

from datetime import datetime
from time import time
import sys


class ManPageGenerator:

    SEC_TITLE = 'TITLE'
    SEC_NAME = 'NAME'
    SEC_SYNOPSIS = 'SYNOPSIS'
    SEC_DESCRIPTION = 'DESCRIPTION'
    SEC_DOCUMENTATION = 'DOCUMENTATION'
    SEC_SEE_ALSO = 'SEE_ALSO'


    def parse_lines_to_dict(self, section_text):
        dict_kv = {}
        section_lines = section_text.split('\n')
        for section_line in section_lines:
            stripped_line = section_line.strip()
            if len(stripped_line) > 0:
                tokens = stripped_line.split('=')
                if len(tokens) > 1:
                    key = tokens[0].strip()
                    value = tokens[1].strip()
                    dict_kv[key] = value
        return dict_kv


    def verify_required_fields(self, section_name, dict_kv, list_keys):
        missing_keys = []
        for req_key in list_keys:
            if req_key not in dict_kv:
                missing_keys.append(req_key)
        if len(missing_keys) > 0:
            print("error: section '%s' missing required fields:" % section_name)
            print('')
            for missing_key in missing_keys:
                print('\t%s' % missing_key)
            sys.exit(1)


    def generate_comments(self):
        ts = time()
        generated_ts = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        txt = '.\" Generated at %s\n' % generated_ts
        txt += '.\" mangenerate.py\n'
        txt += '\n'
        return txt


    def generate_title(self, section_text):
        dict_kv = self.parse_lines_to_dict(section_text)
        self.verify_required_fields(self.SEC_TITLE, dict_kv, ['name',
                                                              'section',
                                                              'footer-center',
                                                              'left-footer',
                                                              'header-center'])
        txt = '.TH %s %s "%s" "%s" "%s"\n' % (dict_kv['name'],
                                              dict_kv['section'],
                                              dict_kv['footer-center'],
                                              dict_kv['left-footer'],
                                              dict_kv['header-center'])
        txt += '\n'
        return txt


    def generate_name(self, section_text):
        dict_kv = self.parse_lines_to_dict(section_text)
        self.verify_required_fields(self.SEC_NAME, dict_kv, ['command',
                                                             'description'])
        txt = '.SH NAME\n'
        txt += '.LP\n'
        txt += '.B %s\n' % dict_kv['command']
        txt += '\- %s\n' % dict_kv['description']
        txt += '\n'
        return txt


    def generate_synopsis(self, section_text):
        dict_kv = self.parse_lines_to_dict(section_text)
        self.verify_required_fields(self.SEC_NAME, dict_kv, ['command',
                                                             'args'])
        txt = '.SH SYNOPSIS\n'
        txt += '.LP\n'
        txt += '.B %s\n' % dict_kv['command']
        txt += '\- %s\n' % dict_kv['args']
        txt += section_text
        return txt


    def generate_description(self, section_text):
        txt = '\n'
        txt += '.SH DESCRIPTION\n'
        txt += '.PP\n'
        txt += section_text
        return txt


    def generate_documentation(self, section_text):
        txt = '\n'
        txt += '.SH DOCUMENTATION\n'
        txt += '.LP\n'
        txt += section_text
        return txt


    def section_text_to_dict(self, section_text):
        dict_section = {}
        section_lines = section_text.split('\n')
        for section_line in section_lines:
            section_line = section_line.strip()
            if len(section_line) > 0:
                line_tokens = section_line.split('=')
                if len(line_tokens) > 1:
                    key = line_tokens[0].strip()
                    value = line_tokens[1].strip()
                    dict_section[key] = value
                else:
                    print("warning: line may be invalid '%s'" % section_line)
        return dict_section


    def generate_man_ref(self, section_name):
        section_text = self.extract_section_text(section_name)
        section_dict = self.section_text_to_dict(section_text)
        if 'name' in section_dict and 'section' in section_dict:
            name = section_dict['name'].strip()
            section_number = section_dict['section'].strip()
            if len(name) > 0 and len(section_number) > 0:
                return '.BR %s(%s)' % (name, section_number)
        return ''


    def generate_see_also(self, section_text):
        txt = '\n'
        txt += '.SH "SEE ALSO"\n'
        txt += '\n'
        section_lines = section_text.split('\n')
        man_refs = []
        for section_line in section_lines:
            section_line = section_line.strip()
            if len(section_line) > 0:
                line_tokens = section_line.split('=')
                if len(line_tokens) > 1:
                    ref_type = line_tokens[0].strip()
                    if ref_type == 'man-ref':
                        ref_section = line_tokens[1].strip()
                        man_refs.append(self.generate_man_ref(ref_section))
                else:
                    print("warning: line may be invalid '%s'" % section_line)
        len_man_refs = len(man_refs)
        last_man_index = len_man_refs - 1
        for i in range(0, len_man_refs):
            if i < last_man_index:
                txt += '%s,\n' % man_refs[i]
            else:
                txt += '%s\n' % man_refs[i]
      
        return txt


    def generate_section(self, section_name, section_text):
        if section_name == self.SEC_TITLE:
            return self.generate_title(section_text)
        elif section_name == self.SEC_NAME:
            return self.generate_name(section_text)
        elif section_name == self.SEC_SYNOPSIS:
            return self.generate_synopsis(section_text)
        elif section_name == self.SEC_DESCRIPTION:
            return self.generate_description(section_text)
        elif section_name == self.SEC_DOCUMENTATION:
            return self.generate_documentation(section_text)
        elif section_name == self.SEC_SEE_ALSO:
            return self.generate_see_also(section_text)
        else:
            return ''


    def extract_section_text(self, section_name):
        section_index = self.list_sections.index(section_name)
        start_line = self.dict_sections[section_name]
        current_line_number = start_line + 1
        max_section_index = len(self.list_sections) - 1
        section_text = ''
        if section_index < max_section_index:
            next_section_name = self.list_sections[section_index+1]
            next_section_start = self.dict_sections[next_section_name]
        else:
            next_section_start = len(self.file_lines)

        for current_line_number in range(start_line, next_section_start-1):
            section_text += self.file_lines[current_line_number]
            section_text += '\n'
            current_line_number += 1
        return section_text


    def process_indent_markup(self, output):
        indent_start_begin_tag = '<indent spaces='
        indent_end_begin_tag = '>'
        indent_end_tag = '</indent>'
        processing_indents = True
        pos_current = 0
        processed_output = ''
        while processing_indents:
            pos_indent_start = output.find(indent_start_begin_tag, pos_current)
            if pos_indent_start > -1:
                pos_search = pos_indent_start + len(indent_start_begin_tag) + 1
                pos_close_tag = output.find(indent_end_begin_tag, pos_search)
                if pos_close_tag > -1:
                    spaces_as_text = output[pos_search:pos_close_tag-1].strip()
                    if len(spaces_as_text) > 0:
                        num_spaces = int(spaces_as_text)
                        pos_start_end_tag = output.find(indent_end_tag,
                                                        pos_close_tag + 1)
                        if pos_start_end_tag > -1:
                            processed_output += output[pos_current:pos_indent_start]
                            processed_output += '.RS %d\n' % num_spaces

                            indented_text = output[pos_close_tag+1:pos_start_end_tag]
                            indented_lines = indented_text.split('\n')

                            for indented_line in indented_lines:
                                if len(indented_line.strip()) > 0:
                                    indented_line = '.IP "%s"\n' % indented_line
                                else:
                                    indented_line = '\n'
                                processed_output += indented_line

                            processed_output += '.RE\n'
                            pos_current = pos_start_end_tag + \
                                          len(indent_end_tag)
                        else:
                            print("error: missing end tag for indent")
                            sys.exit(1)
                    else:
                        print("error: missing 'spaces' attribute for indent")
                        sys.exit(1)
                else:
                    print("error: missing end tag </indent>")
                    sys.exit(1)
            else:
                processing_indents = False

        processed_output += output[pos_current:]

        return processed_output


    def process_markup(self, output, start_tag, end_tag, start_escape, end_escape, markup_type):
        processing = True
        pos_current = 0
        processed_output = ''
        while processing:
            pos_start = output.find(start_tag, pos_current)
            if pos_start > -1:
                pos_end = output.find(end_tag, pos_start + len(start_tag))
                if pos_end > -1:
                    processed_output += output[pos_current:pos_start]
                    marked_text = output[pos_start+len(start_tag):pos_end]
                    processed_output += '%s%s%s' % (start_escape, marked_text, end_escape)
                    pos_current = pos_end + len(end_tag)
                else:
                    print("error: unterminated %s" % markup_type)
                    sys.exit(1)
            else:
                processed_output += output[pos_current:]
                processing = False

        return processed_output


    def process_bold_markup(self, output):
        return self.process_markup(output,
                                   '<b>',
                                   '</b>',
                                   '\\fB',
                                   '\\fR',
                                   'bold')


    def process_underline_markup(self, output):
        return self.process_markup(output,
                                   '<u>',
                                   '</u>',
                                   '\\fI',
                                   '\\fR',
                                   'underline')


    def process_italic_markup(self, output):
        # docs seem to indicate the italic is shown as underline
        return self.process_markup(output,
                                   '<i>',
                                   '</i>',
                                   '\\fI',
                                   '\\fR',
                                   'italic')


    def process_href_markup(self, output):
        href_start = '<a href='
        href_end = '/>'
        processing_links = True
        pos_current = 0
        processed_output = ''
        while processing_links:
            pos_start_href = output.find(href_start, pos_current)
            if pos_start_href > -1:
                search_start = pos_start_href + len(href_start)
                pos_end_href = output.find(href_end, search_start)
                if pos_end_href > -1:
                    # ignore whether there are single quotes or double quotes
                    pos_start_link = pos_start_href + len(href_start) + 1
                    pos_end_link = pos_end_href - 1
                    link_text = output[pos_start_link:pos_end_link]
                    processed_output += output[pos_current:pos_start_href]
                    processed_output += '\n'
                    processed_output += '.BI %s\n' % link_text
                    pos_current = pos_end_href + len(href_end) 
                else:
                    print("error: invalid markup for link (%s...)" % output[pos_start_link:pos_start_link+20])
                    sys.exit(1)
            else:
                processing_links = False

        processed_output += output[pos_current:] 
        output = processed_output

        return output


    def apply_markup(self, output):
        output = self.process_indent_markup(output)
        output = self.process_bold_markup(output)
        output = self.process_underline_markup(output)
        output = self.process_italic_markup(output)
        output = self.process_href_markup(output)
        return output


    def run(self, src_file_path):
        # read file
        with open(src_file_path, 'r') as f:
            self.file_lines = f.readlines()

        # strip out comments and empty lines
        keep_lines = []
        for file_line in self.file_lines:
            stripped_line = file_line.strip()
            if len(stripped_line) == 0 or stripped_line[0] != ';':
                keep_lines.append(stripped_line)
        self.file_lines = keep_lines

        self.list_sections = []
        self.dict_sections = {}
        line_number = 0
        # extract section names
        for file_line in self.file_lines:
            line_number += 1
            stripped_line = file_line.strip()
            if len(stripped_line) > 2:
                len_line = len(stripped_line)
                if stripped_line[0] == '[' and stripped_line[len_line-1] == ']':
                    section_name = stripped_line[1:len_line-1]
                    self.list_sections.append(section_name)
                    self.dict_sections[section_name] = line_number

        missing_sections = []
        required_sections = [self.SEC_TITLE,
                             self.SEC_NAME,
                             self.SEC_SYNOPSIS,
                             self.SEC_DESCRIPTION,
                             self.SEC_DOCUMENTATION]
        # verify required sections
        for req_section in required_sections:
            if req_section not in self.dict_sections:
                missing_sections.append(req_section)

        if len(missing_sections) > 0:
            print('error: the following required sections missing from input file')
            for missing_section in missing_sections:
                print(missing_section)
            sys.exit(1)

        file_text = '\n'.join(self.file_lines)

        # generate each section
        section_index = 0
        max_section_index = len(self.list_sections) - 1

        output = self.generate_comments()

        for section_name in self.list_sections:
            section_text = self.extract_section_text(section_name)
            section_index += 1
            output += self.generate_section(section_name, section_text)

        output = self.apply_markup(output)

        print(output)


if __name__=='__main__':
    if len(sys.argv) < 2:
        print('error: missing file path')
        sys.exit(1)
    man_gen = ManPageGenerator()
    man_gen.run(sys.argv[1])

