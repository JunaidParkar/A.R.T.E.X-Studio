import os
from rich import print
term = os.getenv('TERM', None)
if term == 'cygwin':
    os.environ['TERM'] = 'xterm'


from inquirer import errors
from inquirer.render.console import (
    # Here we need to import these for `ListBoxRender.render_factory()`
    Text, Editor, Password, Confirm, List, Checkbox, Path,
    ConsoleRender as _ConsoleRender,
)
from inquirer.render.console.base import MAX_OPTIONS_DISPLAYED_AT_ONCE
from inquirer.questions import List as ListQuestion
from inquirer import prompt as inquirer_prompt


class ListBoxRender(_ConsoleRender):
    def __init__(self, event_generator=None, theme=None, *args, **kwargs):
        self.render_config = kwargs.pop('render_config', {})
        self._printed_lines = 0
        self.message_handler = self.render_config.pop('message_handler', None)
        super(ListBoxRender, self).__init__(*args, **kwargs)

    def render(self, question, answers=None):
        question.answers = answers or {}

        if question.ignore:
            return question.default

        clazz = self.render_factory(question.kind)
        render = clazz(
            question,
            terminal=self.terminal,
            theme=self._theme,
            show_default=question.show_default,
            render_config=self.render_config,       # customized feature
        )

        self.clear_eos()

        try:
            return self._event_loop(render)
        finally:
            print('')

    def render_factory(self, question_type):
        matrix = {
            'text': Text,
            'editor': Editor,
            'password': Password,
            'confirm': Confirm,
            'list': List,
            'listbox': ListBox,     # added for custom `ListBox` question
            'checkbox': Checkbox,
            'path': Path,
        }

        if question_type not in matrix:
            raise errors.UnknownQuestionTypeError()
        return matrix.get(question_type)

    # added by us
    def _count_lines(self, msg):
        self._printed_lines += msg.count('\n') + 1

    # added by us
    def _reset_counter(self):
        self._printed_lines = 0

    def _print_options(self, render):
        for message, symbol, color in render.get_options():
            if self.message_handler is not None:
                message = self.message_handler(message)

            if hasattr(message, 'decode'):
                message = message.decode('utf-8')
            self._count_lines(message)      # count lines to be erased
            self.print_line(' {color}{s} {m}{t.normal}',
                            m=message, color=color, s=symbol)

    def _print_header(self, render):
        base = render.get_header()

        header = (base[:self.width - 9] + '...'
                  if len(base) > self.width - 6
                  else base)
        default_value = ' ({color}{default}{normal})'.format(
            default=render.question.default,
            color=self._theme.Question.default_color,
            normal=self.terminal.normal
        )
        show_default = render.question.default and render.show_default
        header += default_value if show_default else ''
        msg_template = "{t.move_up}{t.clear_eol}{tq.brackets_color}["\
                       "{tq.mark_color}?{tq.brackets_color}]{t.normal} {msg}"

        self._count_lines(header)       # count lines to be erased
        self.print_str(
            '\n%s:' % (msg_template),
            msg=header,
            lf=not render.title_inline,
            tq=self._theme.Question)

    def _relocate(self):
        # Just get the control code beforehand
        move_up, clear_eol = self.terminal.move_up(), self.terminal.clear_eol()

        # Note that we have to clear lines one by one, so that this function
        # is made for duplicate the control code
        clear_lines = lambda n: (move_up + clear_eol) * n

        if self._printed_lines > 0:
            # Generate control code according to the number of printed lines
            term_refresh_code = clear_lines(self._printed_lines)

            # Print out the control code to erase lines
            print(term_refresh_code, end='', flush=True)
            self._reset_counter()

        self._force_initial_column()
        self._position = 0

class ListBox(List):
    def __init__(self, *args, **kwargs):
        render_config = kwargs.pop('render_config', {})     # custom feature
        self.max_options_in_display = render_config.get(
            'n_max_options', MAX_OPTIONS_DISPLAYED_AT_ONCE
        )
        self.half_options = int((self.max_options_in_display - 1) / 2)
        super(ListBox, self).__init__(*args, **kwargs)

    @property
    def is_long(self):
        choices = self.question.choices or []
        return len(choices) >= self.max_options_in_display   # renamed

    def get_options(self):
        # In order to control the maximal number of choices to show on terminal,
        # we have to override this method and rename every `MAX_OPTIONS_DISPLAYED_AT_ONCE`
        # and `half_options` to `self.max_options_in_display` and `self.half_options`.
        choices = self.question.choices or []
        if self.is_long:
            cmin = 0
            cmax = self.max_options_in_display

            if self.half_options < self.current < len(choices) - self.half_options:
                cmin += self.current - self.half_options
                cmax += self.current - self.half_options
            elif self.current >= len(choices) - self.half_options:
                cmin += len(choices) - self.max_options_in_display
                cmax += len(choices)

            cchoices = choices[cmin:cmax]
        else:
            cchoices = choices

        ending_milestone = max(len(choices) - self.half_options, self.half_options + 1)
        is_in_beginning = self.current <= self.half_options
        is_in_middle = self.half_options < self.current < ending_milestone
        is_in_end = self.current >= ending_milestone

        for index, choice in enumerate(cchoices):
            end_index = ending_milestone + index - self.half_options - 1
            if (is_in_middle and index == self.half_options) \
                    or (is_in_beginning and index == self.current) \
                    or (is_in_end and end_index == self.current):

                color = self.theme.List.selection_color
                symbol = self.theme.List.selection_cursor
            else:
                color = self.theme.List.unselected_color
                symbol = ' '
            yield choice, symbol, color


class ListBoxQuestion(ListQuestion):
    kind = 'listbox'

    def __init__(self, name, **kwargs):
        super(ListBoxQuestion, self).__init__(name, **kwargs)


# ----- Things for using those component above -----
from datetime import datetime as dt
import textwrap as tw


class Note(object):
    def __init__(self, title, content, create_time):
        self.title = title
        self.content = content
        self.create_time = create_time

    def __repr__(self):
        return '<Note object, title: %s>' % self.title

    @classmethod
    def create(cls, title, content):
        return cls(title, content, dt.now().timestamp())


class NoteFormatter(object):
    def __init__(self, **kwargs):
        self.config = {
            'width': kwargs.get('width', 70),
            'tabsize': kwargs.get('tabsize', 4),
            'replace_whitespace': kwargs.get('replace_whitespace', False),
            'drop_whitespace': kwargs.get('drop_whitespace', True),
            'max_lines': kwargs.get('max_lines', 3),
            'placeholder': kwargs.get('placeholder', '...'),
            'initial_indent': kwargs.get('initial_indent', '    '),
            'subsequent_indent': kwargs.get('subsequent_indent', '    '),
        }
        self.text_wrapper = tw.TextWrapper(**self.config)
        self._prepare_formatter()

    def _prepare_formatter(self):
        text_shortener = lambda text: tw.shorten(
            text, width=self.config['width'], placeholder='...'
        )
        text_indenter = lambda text: '\n'.join(self.text_wrapper.wrap(text))

        fmt_title = lambda x: 'Title: %s' % text_shortener(x.title)
        fmt_content = lambda x: 'Content:\n%s' % text_indenter(x.content)
        fmt_create_time = lambda x: 'Created: %s' % (
            dt.fromtimestamp(x.create_time).strftime('%Y-%m-%d %H:%M:%S')
        )
        self.formatters = [fmt_title, fmt_create_time, fmt_content]

    def __call__(self, note):
        return '\n'.join([fmt(note) for fmt in self.formatters])
