{% autoescape off %}
{% if file_browser %}
function CustomFileBrowser(field_name, url, type, win) {
    // alert("Field_Name: " + field_name + "\nURL: " + url + "\nType: " + type + "\nWin: " + win); // debug/testing
    var fileBrowserWindow = new Array();

    fileBrowserWindow['title'] = 'File Browser';
    fileBrowserWindow['file'] = "/admin/filebrowser/?pop=2";
    fileBrowserWindow['width'] = '820';
    fileBrowserWindow['height'] = '600';
    fileBrowserWindow['close_previous'] = 'no';
    tinyMCE.openWindow(fileBrowserWindow, {
      window : win,
      input : field_name,
      resizable : 'yes',
      scrollbars : 'yes',
      inline : 'yes',
      editorID: tinyMCE.getWindowArg('editor_id')
    });
    return false;
}
{% endif %}
tinyMCE.init({
	mode : "{{ mode }}",
    apply_source_formatting : true,
    entity_encoding : "raw",
    {% ifequal mode "exact" %}elements : "{{ elements }}",{% endifequal %}
    {% if height %}height : "{{ height }}",{% endif %}
    {% if width %}width : "{{ width }}",{% endif %}
	theme : "{{ theme }}",
    language : "{{ language }}",
	{% if content_css %}content_css : "{{ content_css }}",{% endif %}
	{% if editor_css %}editor_css : "{{ editor_css }}",{% endif %}
    {% if debug %}debug : "{{ debug }}",{% endif %}

// Save
    save_enablewhendirty : true,
    save_on_tinymce_forms: true,

// XHTML
	extended_valid_elements : "{{ extended_valid_elements }}",
    invalid_elements : "{{ invalid_elements }}",
    convert_fonts_to_spans : true,
    forced_root_block : {% if forced_root_block %}"{{ forced_root_block }}"{% else %}false{% endif %},
    fix_table_elements : true,
    fix_list_elements : true,

// theme advanced
	theme_advanced_toolbar_location : "top",
	theme_advanced_toolbar_align : "left",
	theme_advanced_buttons1 : "{{ theme_advanced_buttons1 }}",
	theme_advanced_buttons2 : "{{ theme_advanced_buttons2 }}",
	theme_advanced_buttons3 : "{{ theme_advanced_buttons3 }}",
	theme_advanced_buttons1_add : "{{ theme_advanced_buttons1_add }}",
	theme_advanced_buttons2_add : "{{ theme_advanced_buttons2_add }}",
	theme_advanced_buttons3_add : "{{ theme_advanced_buttons3_add }}",
    theme_advanced_blockformats : "p,h2,h3,h4",
    theme_advanced_styles : "{% for style in theme_advanced_styles %}{{ style.description }}={{ style.css_class }}{% if not forloop.last %};{% endif %}{% endfor %}",
    theme_advanced_statusbar_location : "bottom",
    theme_advanced_resizing : {{ theme_advanced_resizing|yesno:"true,false" }},
    theme_advanced_path : {{ theme_advanced_path|yesno:"true,false" }},

// fullscreen
    fullscreen_settings : {
		theme_advanced_path_location : "top",
		theme_advanced_buttons1 : "preview,separator,cut,copy,paste,separator,undo,redo,separator,search,replace,separator,code,separator,cleanup,separator,bold,italic,underline,strikethrough,separator,forecolor,backcolor,separator,justifyleft,justifycenter,justifyright,justifyfull,separator,help",
		theme_advanced_buttons2 : "removeformat,styleselect,formatselect,fontselect,fontsizeselect,separator,bullist,numlist,outdent,indent,separator,link,unlink,anchor",
		theme_advanced_buttons3 : "sub,sup,separator,image,insertdate,inserttime,separator,tablecontrols,separator,hr,advhr,visualaid,separator,charmap,emotions,iespell,flash,separator,print"
	},

// plugins
	plugins : "{{ plugins }}",
	plugin_insertdate_dateFormat : "%d.%m.%Y",
	plugin_insertdate_timeFormat : "%H:%M:%S",

// Advimage
    advimage_styles : "{% for style in advimage_styles %}{{ style.description }}={{ style.css_class }}{% if not forloop.last %};{% endif %}{% endfor %}",
    advimage_update_dimensions_onchange: true,
    
// Advlink
    advlink_styles : "{% for style in advlink_styles %}{{ style.description }}={{ style.css_class }}{% if not forloop.last %};{% endif %}{% endfor %}",
    external_link_list_url : "/tinymce/tiny_mce_links.js",

    {% if file_browser %}
// FileBrowser
    file_browser_callback : "CustomFileBrowser",
    relative_urls : false,
    {% endif %}
    
// template
	template_cdate_classes : "cdate creationdate",
	template_mdate_classes : "mdate modifieddate",
	template_selected_content_classes : "selcontent",
	template_cdate_format : "%m/%d/%Y : %H:%M:%S",
	template_mdate_format : "%m/%d/%Y : %H:%M:%S",
	template_replace_values : {},
	template_templates : [
    {% for template in templates %}
		{
			title : "{{ template.title }}",
			src : "/tinymce/templates/{{ template.name }}",
			description : "{{ template.description }}"
		}{% if not forloop.last %},{% endif %}
    {% endfor %}
    ]
});
{% endautoescape %}