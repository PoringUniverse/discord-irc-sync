import re
from .utils import replace_all

IRC_BOLD, IRC_ITALIC, IRC_UNDERLINE, IRC_RESET = ("\x02","\x1d", "\x1f", "\x0f")
DSC_BOLD, DSC_ITALIC, DSC_UNDERLINE = ("**","*","__")

class D2IFormatter():

    syntax = {
        'double_emphasis': {
            're': re.compile(r'(\*{2})([\s\S]+?)(\*{2})(?!\*)'),
            'irc': IRC_BOLD,
            'discord': DSC_BOLD 
        },
        'emphasis': {
            're': re.compile(
                r'\b(_)((?:__|[^_])+?)(_)\b'  # _word_
                r'|'
                r'(\*)((?:\*\*|[^\*])+?)(\*)(?!\*)'  # *word*
            ),
            'irc': IRC_ITALIC,
            'discord': DSC_ITALIC
        },
        'underline': {
            're': re.compile(r'(_{2})([\s\S]+?)(_{2})(?!_)'),
            'irc': IRC_UNDERLINE,
            'discord': DSC_UNDERLINE
        }
    }

    rules = ['double_emphasis', 'emphasis', 'underline']

    def replace_double_emphasis(self, matchobj):
        return self.syntax['double_emphasis']['irc'] + matchobj.group(2) + self.syntax['double_emphasis']['irc'] 

    def replace_emphasis(self, matchobj):
        if matchobj.group(2):
            res = matchobj.group(2)
        else:
            res = matchobj.group(5)
        return self.syntax['emphasis']['irc'] + res + self.syntax['emphasis']['irc'] 

    def replace_underline(self, matchobj):
        return self.syntax['underline']['irc'] + matchobj.group(2) + self.syntax['underline']['irc'] 


    def format(self, message):
        for rule in self.rules:
            regex = self.syntax[rule]['re']
            m = regex.search(message)
            if m is not None:
                message = regex.sub(getattr(self, 'replace_%s' % rule), message)
        return message

class I2DFormatter: # @TODO

    def sanitize(self, message):
        replacements = [('\\','\\\\'), ('*','\\*'), ('_','\\_')]
        message = replace_all(message, replacements)
        return re.sub(
                r'\x03\d{2}(?:,\d{2})'
                r'|'
                r'['+ IRC_BOLD + IRC_UNDERLINE + IRC_ITALIC + IRC_RESET +']',
                '',
                message)

    def format(self, message):
        message = self.sanitize(message)
        char_list = [(c,0) for c in message]
        counter = 0
        while counter < len(char_list):
            char_tuple=char_list[counter]
            
            if char_tuple[0] in self.symbols: # Formatting character
                del char_list[counter]
                for i in range(counter, len(char_list)):
                    if self.symbols[char_tuple[0]]:
                        char_list[i] = (char_list[i][0], char_list[i][1]^self.symbols[char_tuple[0]])
                    else:
                        char_list[i] = (char_list[i][0], 0)
            else: # Common character. Goto next one
                counter+=1
        res = ""
        add = []
        for key, char_tuple in enumerate(char_list):
            if key == 0:
                if char_tuple[1] & self.B_FLAG:
                    add.append(DSC_BOLD)
                if char_tuple[1] & self.I_FLAG:
                    add.append(DSC_ITALIC)
                if char_tuple[1] & self.U_FLAG:
                    add.append(DSC_UNDERLINE)
            else:
                if char_tuple[1] & self.B_FLAG ^ char_list[key-1][1] & self.B_FLAG:
                    add.append(DSC_BOLD)
                if char_tuple[1] & self.I_FLAG ^ char_list[key-1][1] & self.I_FLAG:
                    add.append(DSC_ITALIC)
                if char_tuple[1] & self.U_FLAG ^ char_list[key-1][1] & self.U_FLAG:
                    add.append(DSC_UNDERLINE)
            print(add)
            add = []
        print(res)
