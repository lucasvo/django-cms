var FormId = {
    get: function(id) { return id; }
};
var Form = new Class({
    initialize: function(template, value) {
        if (Form.instances == undefined)
            Form.instances = 0;
        this.id = ++Form.instances;
        if (value)
            template = value;
        else
            template = template.slice(); // create a copy
        for (var i=0; i<template.length; i++)
            if (template[i] instanceof Object)
                template[i] = template[i].get(this.id);
        this.html = template.join('');
    }
});

