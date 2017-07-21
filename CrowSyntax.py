import sys
import re
from PyQt4.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

def format(color, style=' '):
    """Regresa un valor QTextCharFormat con el formato requerido"""
    
    _color = QColor()
    _color.setNamedColor(color)
    
    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeigh(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)
    
    return _format
    
STYLES = {
    'math': format('darkGreen'),
    'comment': format('Gray'),
    'comand': format('Blue'),
    'packege': format('Orange')
}    
 
class LatexHighlighter(QSyntaxHighlighter):
    """Resaltador de sintaxis para LaTeX"""
    
    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)
        #Elementos que son multilinea
        self.math_mode_1 = (re.compile('(?<!\\\\)\$'), 1, STYLES['math'])
        
        rules = []
        
        rules +=[
            # Nombre de los Paquetes
            (r'(?<=\{).*?(?=\})', STYLES['packege']),
            # Comandos empezando por \
            (r'\\[A-Z,a-z]*', STYLES['comand']),
            # Comentarios 
            (r'%[^\n]*', STYLES['comment'])
        ]
        
        #Crea un valor QRegExp para cada regla        
        self.rules = [(re.compile(pat), fmt)
            for(pat, fmt) in rules]
    
    #Sobreescribe el metodo original de QSyntaxHighlighter
    def highlightBlock(self, text):
        """Aplica resaltado de sintaxis a un bloque dado de texto"""
         
        for expression, _format in self.rules:
            self.general_syntax(text,expression,_format)
                
        self.setCurrentBlockState(0)
        self.math_mode(text,*self.math_mode_1)
    
    def general_syntax(self,text,expression, _format):
        tex = str(text)
        match = expression.search(tex)
        if match is not None:
            index = match.start()
        else:
            index = -1         
        
        while index >= 0:
            length = len(match.group(0))
            self.setFormat(index, length, _format)
            match = expression.search(text, index + length)    
            if match is not None:
                index = match.start()
            else:
                index = -1         
            
    
    def math_mode(self, text, reg_exp, in_state, style):
        tex = str(text)
        
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        else:    
            match = reg_exp.search(tex)
            if match is not None:
                start = match.start()
                add = match.end() - match.start()
            else:
                start = -1
                add = 0                
        
        while start >= 0:
            match = reg_exp.search(tex,start + add)
            
            if match is not None:
                end = match.start()
            else:
                end = -1          
            
            if end >= add:
                length = end - start + match.end()-match.start() 
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(in_state)
                length = len(tex) - start
                
            self.setFormat(start,length, style)
            
            match = reg_exp.search(tex,start + length)
            if match is not None:
                start = match.start()
            else:
                start = -1 

