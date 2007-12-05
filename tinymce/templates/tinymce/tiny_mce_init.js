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

// theme advanced
	theme_advanced_toolbar_location : "top",
	theme_advanced_toolbar_align : "left",
	theme_advanced_buttons1 : "fullscreen,separator,template,separator,bold,italic,underline,strikethrough,separator,bullist,numlist,separator,undo,redo,separator,link,unlink,anchor,separator,image,cleanup,help,separator,code",
	theme_advanced_buttons2 : "search,replace,separator,removeformat,formatselect,styleselect",
	theme_advanced_buttons3 : "",

// fullscreen
    fullscreen_settings : {
		theme_advanced_path_location : "top",
		theme_advanced_buttons1 : "fullscreen,separator,preview,separator,cut,copy,paste,separator,undo,redo,separator,search,replace,separator,code,separator,cleanup,separator,bold,italic,underline,strikethrough,separator,forecolor,backcolor,separator,justifyleft,justifycenter,justifyright,justifyfull,separator,help",
		theme_advanced_buttons2 : "removeformat,styleselect,formatselect,fontselect,fontsizeselect,separator,bullist,numlist,outdent,indent,separator,link,unlink,anchor",
		theme_advanced_buttons3 : "sub,sup,separator,image,insertdate,inserttime,separator,tablecontrols,separator,hr,advhr,visualaid,separator,charmap,emotions,iespell,flash,separator,print"
	},

	auto_cleanup_word : true,

// plugins
	plugins : "{{ plugins }}",
	plugin_insertdate_dateFormat : "%d.%m.%Y",
	plugin_insertdate_timeFormat : "%H:%M:%S",
	extended_valid_elements : "{{ extended_valid_elements }}",
    convert_fonts_to_spans : true,
    forced_root_block : {% if forced_root_block %}"{{ forced_root_block }}"{% else %}false{% endif %},

// FileBrowser
    advimage_styles : "{% for style in advimage_styles %}{{ style.description }}={{ style.css_class }}{% if not forloop.last %};{% endif %}{% endfor %}",
    advlink_styles : "{% for style in advlink_styles %}{{ style.description }}={{ style.css_class }}{% if not forloop.last %};{% endif %}{% endfor %}",
    advimage_update_dimensions_onchange: true,
    {% if file_browser %}
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
