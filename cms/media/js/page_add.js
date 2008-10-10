// mootools: Window.DomReady, Element.Selectors, Element.Dimensions, Json.Remote, Tips

var PageContent = Form.extend({
    initialize: function(value){
        this.parent(PageContent.template, value);
        this.fieldset = new Element('fieldset');
        this.fieldset.setProperty('class', 'module aligned');
        this.fieldset.innerHTML = this.html;
        $('page-contents').adopt(this.fieldset);
        if (typeof(use_tinymce) != 'undefined' && use_tinymce) {
    		tinyMCE.execCommand('mceAddControl', false, "id_pagecontent-content." + this.id);
        }

        var that = this;
        setTimeout(function(){
            $ES('h2', that.fieldset).addEvent('click', function(event) {
                    $ES('.pagecontent-content', that.fieldset).toggleClass('hidden');
                    new Event(event).preventDefault();
                });
            $ES('a.toggle-advanced', that.fieldset).addEvent('click', function(event) {
                    $ES('div.advanced', that.fieldset).toggleClass('hidden');
                    $ES('a.toggle-advanced', that.fieldset).toggleClass('hidden');
                    new Event(event).preventDefault();
                });
            $ES('a.pagecontent-delete', that.fieldset).addEvent('click', function(event) {
                var event = new Event(event);
                var re = new RegExp('(\\d+)');
                var id = re.exec(event.target.getAttribute('href'))[0];
                event.preventDefault();
                var value = $E('h2', that.fieldset).childNodes[0].nodeValue;
                var confirmed = confirm('Are you sure you want delete the following content?\nIt will be deleted immediately.\n"'+value+'"');
                if (confirmed)
                {
                    new Json.Remote('../../page/content/json/', { onComplete: function(obj) {
                        if (!obj['error']) {
                            event.target.parentNode.parentNode.parentNode.parentNode.remove();
                        } else { alert(obj['error']); }
                    }}).send({'action':'delete', 'id':id});
                }
            });
            $ES('a.pagecontent-preview', that.fieldset).addEvent('click', function(event) {
                var event = new Event(event);
                var form = $('page-form');
                form.target = '_blank';
                form.action = 'preview/';
                var preview = new Element('input').setProperties({'type':'hidden', 'name':'preview', 'value':that.id});
                form.adopt(preview)
                form.submit();
                form.target = '';
                form.action = '';
                preview.remove();
                event.preventDefault();
            });
            //if (value && that.id > 1)
                //$ES('.pagecontent-content', that.fieldset).toggleClass('hidden');
        }, 0);
    }
});

function str2url(str)
{
    str = str.toUpperCase();
    str = str.toLowerCase();

    str = str.replace(/[\u00E0\u00E1\u00E2\u00E3\u00E4\u00E5]/g,'a');
    str = str.replace(/[\u00E7]/g,'c');
    str = str.replace(/[\u00E8\u00E9\u00EA\u00EB]/g,'e');
    str = str.replace(/[\u00EC\u00ED\u00EE\u00EF]/g,'i');
    str = str.replace(/[\u00F2\u00F3\u00F4\u00F5\u00F6\u00F8]/g,'o');
    str = str.replace(/[\u00F9\u00FA\u00FB\u00FC]/g,'u');
    str = str.replace(/[\u00FD\u00FF]/g,'y');
    str = str.replace(/[\u00F1]/g,'n');
    str = str.replace(/[\u0153]/g,'oe');
    str = str.replace(/[\u00E6]/g,'ae');
    str = str.replace(/[\u00DF]/g,'ss');

    str = str.replace(/[^a-z0-9_\s\'\:\/\[\]-]/g,'');
    //str = trim(str); ?
    str = str.replace(/^\s+|\s+$/g, ''); // trim leading/trailing spaces
    str = str.replace(/[\s\'\:\/\[\]-]+/g,' ');
    str = str.replace(/[ ]/g,'-');

    return str;
}

Window.onDomReady(function(){
    $$('.navigation-delete').addEvents({
        'click':function(event) {
            var event = new Event(event);
            var re = new RegExp('(\\d+)');
            var id = re.exec(event.target.getAttribute('href'))[0];
            event.preventDefault();
            var confirmed = confirm('Are you sure you want remove this page from\n"'+event.target.parentNode.childNodes[0].nodeValue+'"? It will be removed immediately.');
            if (confirmed)
            {
                new Json.Remote('../../navigation/json/', { onComplete: function(obj) {
                    if (!obj['error']) {
                        var p = event.target.parentNode;
                        if ($ES('li', p.parentNode).length == 1)
                            p.parentNode.parentNode.remove();
                        else
                            event.target.parentNode.remove()
                    } else { alert(obj['error']); }
                }}).send({'action':'delete', 'id':id});
            }
        }
    });
    $$('.page-content-add').addEvents({
        'click':function(event) {
            new PageContent();
            new Event(event).preventDefault();
        }
    });
    var title = $('id_title');
    var slug = $('id_slug');
    if (!slug.value)
    {
        title.addEvents({
            'keyup':function(event) { if (!slug._changed) slug.value = str2url(title.value); },
            'change':function(event) { if (!slug._changed) slug.value = str2url(title.value); }
        });
        slug.addEvents({
            'change':function(event) { slug._changed = true; }
        });
    }
})
