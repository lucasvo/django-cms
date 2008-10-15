var NavigationNested = Nested.extend({
    start: function(event) {
        event = new Event(event);
        if (event.target.nodeName == 'SPAN')
            this.parent(event);
    }
});

Window.onDomReady(function(){
    var rootError = new Element('div').setProperty('id', 'root-error');
    rootError.innerHTML = '<ul class="errorlist"><li>' + gettext('There must not be more than one root element. Please reorder the pages so that there is only one root element.') + '</li></ul>';
    rootError.addClass('hidden');
    $('errors').adopt(rootError);
    var sortIt = new NavigationNested('navigation', {
        collapse: false,
        onStart: function(el) {
            el.addClass('drag');
        },
        onComplete: function(el) {
            el.removeClass('drag');
            var newSerialized = sortIt.serialize();
            if (Json.toString(sortIt.lastSerialized) != Json.toString(newSerialized))
                el.addClass('changed');
            this.lastSerialized = newSerialized;
            if (newSerialized.length == 1)
                rootError.addClass('hidden');
            else
                rootError.removeClass('hidden');
        }
    });
    var down_date;
    var form = $('navigation-form');
    form.addEvent('submit', function() {
        form.adopt(new Element('input').setProperties({'type': 'hidden', 'name': 'navigation', 'value':Json.toString(sortIt.lastSerialized)}));
    });
    $$('#navigation .toolbox').addEvent('click', function(event) {
        //event.stop();
        //event.preventDefault();
        //event.stopPropagation();
    });
    $$('#navigation li>a').addEvent('mousedown', function(event) {
        down_date = new Date().getTime();
    });
    $$('#navigation li>a').addEvent('click', function(event) {
        var delta = (new Date()-down_date);
        if (delta > 400)
            event.preventDefault();
    });
    sortIt.lastSerialized = sortIt.serialize();
});


