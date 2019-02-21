"""Convert FLEx interlinear on clipboard, to LaTeX code on clipboard."""

import pyperclip

# TODO:
#   gb4e format
#   avoid using textsc{} on capitalized proper nouns
#   more flexible interpretation of FLEx fields besides Word and Word Gloss
#   check for punctuation mark as last item of interlinear before removing


class Interlinear(object):
    """Represents an interlinear example."""

    FORMAT = 'myexpex'
    NEWLINE = '\n'

    def __init__(self):
        self.get_flex()
        self.parse_flex()

    def get_flex(self):
        """Retrieve text from clipboard."""

        self.flex = pyperclip.paste()

    def parse_flex(self):
        """Parse the text from FLEx."""

        lines = self.flex.splitlines()
        if not lines or len(lines)==1:
            print('No interlinear found on clipboard')
            pass

        for line in lines:
            tabsplit = line.split('\t')
            if len(tabsplit) > 1:
                if tabsplit[0].isnumeric():
                    # number
                    self.exampleno = int(tabsplit[0])
                    if tabsplit[1].lower() == 'Word'.lower():
                        self.word = tabsplit[2:-1]  # assumes punctuation mark
                    elif tabsplit[1].lower() == 'Word Gloss'.lower():
                        self.gloss = tabsplit[2:-1]
                elif not tabsplit[0]:
                    # empty string
                    if tabsplit[1].lower() == 'Word'.lower():
                        self.word = tabsplit[2:-1]
                    elif tabsplit[1].lower() == 'Word Gloss'.lower():
                        self.gloss = tabsplit[2:-1]
                elif tabsplit[0].lower() == 'Word'.lower():
                    self.word = tabsplit[1:-1]
                elif tabsplit[0].lower() == 'Word Gloss'.lower():
                    self.gloss = tabsplit[1:-1]
                else:
                    raise Exception("Can't recognize label on text")

            elif len(tabsplit) == 1:
                # should be Free Translation
                cleanline = line.replace('\u200e','')
                assert 'Free' in cleanline
                pos = cleanline.find('Free') + 4
                cleanline2 = cleanline[pos:].lstrip()
                self.free = "`{}'".format(cleanline2)

            else:
                raise Exception('empty line?')

    def construct_tex(self):
        """Create code for LaTeX."""

        output = []

        for i, w in enumerate(self.word):
            if ' ' in w:
                self.word[i] = '{' + w + '}'

        for i, g in enumerate(self.gloss):
            if ' ' in g:
                g = '{' + g + '}'
            if g == '':
                g = '{}'
            newg = ''
            nowupper = False
            for j in range(len(g)):
                if g[j].islower() and nowupper:
                    newg += '}' + g[j]
                    nowupper = False
                elif g[j].isupper() and not nowupper:
                    newg += '\\textsc{' + g[j].lower()
                    nowupper = True
                elif g[j].isupper() and nowupper:
                    newg += g[j].lower()
                else:
                    newg += g[j]
            if nowupper:
                newg += '}'
            self.gloss[i] = newg

        if self.FORMAT.lower() == 'myexpex':
            line = '\\begin{exa}'
            output.append(line)

            line = '  \\begingl'
            output.append(line)

            tmp = ' '.join(self.word)
            line = '    ' + ' '.join(('\\gla', tmp, '//'))
            output.append(line)

            tmp = ' '.join(self.gloss)
            line = '    ' + ' '.join(('\\glb', tmp, '//'))
            output.append(line)

            if hasattr(self, 'free'):
                line = '    ' + ' '.join(('\\glft', self.free, '//'))
                output.append(line)

            line = '  \\endgl'
            output.append(line)

            line = '\\end{exa}%'
            output.append(line)

            output.append('')
            output.append('')

            self.output = output

    def copy_output(self):
        """Copy output text to clipboard."""

        pyperclip.copy(self.NEWLINE.join(self.output))


if __name__ == '__main__':
    """Do everything automatically."""

    il = Interlinear()
    il.construct_tex()
    il.copy_output()
