from django import template

register = template.Library()

def background(parser, token):
    try:
        tag_name, path, width, height = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly three arguments (path, width, height)" % token.contents[0]
    nodelist = parser.parse(('endbackground',))
    parser.delete_first_token()
    return BackgroundNode(nodelist, path, width, height)
background = register.tag(background)

class BackgroundNode(template.Node):
    def __init__(self, nodelist, path, width, height):
        self.nodelist = nodelist
        self.path = path
        self.width = width
        self.height = height
    def render(self, context):
        path = template.resolve_variable(self.path, context)
        width = template.resolve_variable(self.width, context)
        height = template.resolve_variable(self.height, context)
        output = self.nodelist.render(context)
        return '<div class="background" style="background-image:url(%s); width:%spx; height:%spx;">\n\n<div>%s\n</div>\n\n</div>' % (path, width, height, output) 

def word_slice(value, arg):
    words = value.split(' ')
    args = arg.split(':')
    if len(args) > 1:
        if args[0] and args[1]:
            out = words[int(args[0]):int(args[1])]
        elif args[0]:
            out = words[int(args[0]):]
        elif args[1]:
            out = words[int(args[1]):]
        else:
            out = words
    else:
        out = words[int(args[0])]
    return ' '.join(out)
register.filter('cms_word_slice', word_slice)
    
def at(value, arg):
    try:
        return value and value[arg] or ''
    except IndexError:
        return ''
register.filter('cms_at', at)
