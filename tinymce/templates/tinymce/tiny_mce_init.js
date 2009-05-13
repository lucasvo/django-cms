function CustomFileBrowser(field_name, url, type, win) {

    var cmsURL = "/admin/filebrowser/?pop=2";
    cmsURL = cmsURL + "&type=" + type;
    
    tinyMCE.activeEditor.windowManager.open({
        file: cmsURL,
        width: 820,  // Your dimensions may differ - toy around with them!
        height: 500,
        resizable: "yes",
        scrollbars: "yes",
        inline: "no",  // This parameter only has an effect if you use the inlinepopups plugin!
        close_previous: "no",
    }, {
        window: win,
        input: field_name,
        editor_id: tinyMCE.selectedInstance.editorId,
    });
    return false;
}

tinyMCE.init({
    mode : "specific_textareas",
    editor_selector : "mceEditor",
    apply_source_formatting : true,
    entity_encoding : "raw",
    
    height : "400",
    width : "480",
	theme : "advanced",
    language : "{{ language }}",
	
	
    

// Save
    save_enablewhendirty : true,
    save_on_tinymce_forms: true,

// XHTML
	extended_valid_elements : "a[class|name|href|titlet|target|onclick],img[class|style|src|alt=image|title|onmouseover|onmouseout|width|height],p[id|style|dir|class],span[class|style]",
    invalid_elements : "",
    convert_fonts_to_spans : true,
    forced_root_block : false,
    fix_table_elements : true,
    fix_list_elements : true,

// theme advanced
	theme_advanced_toolbar_location : "top",
	theme_advanced_toolbar_align : "left",
	theme_advanced_buttons1 : "save,template,separator,copy,pastetext,pasteword,separator,undo,redo,separator,search,replace,separator,cleanup,code,fullscreen, cleanup",
	theme_advanced_buttons2 : "formatselect,removeformat,fontselect,fontsizeselect,separator,bold,italic,separator,justifyleft,justifycenter,justifyright,justifyfull,separator, bullist,numlist,separator,forecolor,backcolor,",
	theme_advanced_buttons3 : "link,unlink,anchor,separator,hr,image, media,separator,tablecontrols,separator,visualchars,nonbreaking,",
	theme_advanced_buttons1_add : "",
	theme_advanced_buttons2_add : "",
	theme_advanced_buttons3_add : "",
    theme_advanced_blockformats : "p,h2,h3,h4",
    theme_advanced_styles : "",
    theme_advanced_statusbar_location : "bottom",
    theme_advanced_resizing : true,
    theme_advanced_path : true,

// fullscreen
    fullscreen_settings : {
		theme_advanced_path_location : "top",
/*		theme_advanced_buttons1 : "preview,separator,cut,copy,paste,separator,undo,redo,separator,search,replace,separator,code,separator,cleanup,separator,bold,italic,underline,strikethrough,separator,forecolor,backcolor,separator,justifyleft,justifycenter,justifyright,justifyfull,separator,help",
		theme_advanced_buttons2 : "removeformat,styleselect,formatselect,fontselect,fontsizeselect,separator,bullist,numlist,outdent,indent,separator,link,unlink,anchor",
		theme_advanced_buttons3 : "sub,sup,separator,image,insertdate,inserttime,separator,tablecontrols,separator,hr,advhr,visualaid,separator,charmap,emotions,iespell,flash,separator,print"
*/	},

// plugins
	plugins : "advimage,advlink,table,searchreplace,contextmenu,template,paste,save,autosave,visualchars,nonbreaking,fullscreen",
	plugin_insertdate_dateFormat : "%d.%m.%Y",
	plugin_insertdate_timeFormat : "%H:%M:%S",

// Advimage
    advimage_styles : "",
    advimage_update_dimensions_onchange: true,
    
// Advlink
    advlink_styles : "",
    external_link_list_url : "/tinymce/tiny_mce_links.js",

    
// FileBrowser
    file_browser_callback : "CustomFileBrowser",
    relative_urls : false,
    
    
// template
	template_cdate_classes : "cdate creationdate",
	template_mdate_classes : "mdate modifieddate",
	template_selected_content_classes : "selcontent",
	template_cdate_format : "%m/%d/%Y : %H:%M:%S",
	template_mdate_format : "%m/%d/%Y : %H:%M:%S",
	template_replace_values : {},
	template_templates : [
    
    ]
});

 
{% comment %}
function CustomFileBrowser(field_name, url, type, win) {

    var cmsURL = "/admin/filebrowser/?pop=2";
    cmsURL = cmsURL + "&type=" + type;
    
    tinyMCE.activeEditor.windowManager.open({
        file: cmsURL,
        width: 820,  // Your dimensions may differ - toy around with them!
        height: 500,
        resizable: "yes",
        scrollbars: "yes",
        inline: "no",  // This parameter only has an effect if you use the inlinepopups plugin!
        close_previous: "no",
    }, {
        window: win,
        input: field_name,
        editor_id: tinyMCE.selectedInstance.editorId,
    });
    return false;
}

tinyMCE.init({
    mode : "specific_textareas",
    editor_selector : "mceEditor",
    apply_source_formatting : true,
    entity_encoding : "raw",
    
    height : "400",
    width : "480",
	theme : "advanced",
    language : "en" /*"de",*/,
	
	
    

// Save
    save_enablewhendirty : true,
    save_on_tinymce_forms: true,

// XHTML
	extended_valid_elements : "a[class|name|href|titlet|target|onclick],img[class|style|src|alt=image|title|onmouseover|onmouseout],p[id|style|dir|class],span[class|style]",
    invalid_elements : "",
    convert_fonts_to_spans : true,
    forced_root_block : false,
    fix_table_elements : true,
    fix_list_elements : true,

// theme advanced
	theme_advanced_toolbar_location : "top",
	theme_advanced_toolbar_align : "left",
	theme_advanced_buttons1 : "save,template,separator,copy,pastetext,pasteword,separator,undo,redo,separator,search,replace,separator,cleanup,code,fullscreen, cleanup",
	theme_advanced_buttons2 : "formatselect,removeformat,fontselect,fontsizeselect,separator,bold,italic,separator,justifyleft,justifycenter,justifyright,justifyfull,separator, bullist,numlist,separator,forecolor,backcolor,",
	theme_advanced_buttons3 : "link,unlink,anchor,separator,hr,image, media,separator,tablecontrols,separator,visualchars,nonbreaking,",
	theme_advanced_buttons1_add : "",
	theme_advanced_buttons2_add : "",
	theme_advanced_buttons3_add : "",
    theme_advanced_blockformats : "p,h2,h3,h4",
    theme_advanced_styles : "",
    theme_advanced_statusbar_location : "bottom",
    theme_advanced_resizing : true,
    theme_advanced_path : true,

// fullscreen
    fullscreen_settings : {
		theme_advanced_path_location : "top",
/*		theme_advanced_buttons1 : "preview,separator,cut,copy,paste,separator,undo,redo,separator,search,replace,separator,code,separator,cleanup,separator,bold,italic,underline,strikethrough,separator,forecolor,backcolor,separator,justifyleft,justifycenter,justifyright,justifyfull,separator,help",
		theme_advanced_buttons2 : "removeformat,styleselect,formatselect,fontselect,fontsizeselect,separator,bullist,numlist,outdent,indent,separator,link,unlink,anchor",
		theme_advanced_buttons3 : "sub,sup,separator,image,insertdate,inserttime,separator,tablecontrols,separator,hr,advhr,visualaid,separator,charmap,emotions,iespell,flash,separator,print"
*/	},

// plugins
	plugins : "advimage,advlink,table,searchreplace,contextmenu,template,paste,save,autosave,visualchars,nonbreaking,fullscreen",
	plugin_insertdate_dateFormat : "%d.%m.%Y",
	plugin_insertdate_timeFormat : "%H:%M:%S",

// Advimage
    advimage_styles : "",
    advimage_update_dimensions_onchange: true,
    
// Advlink
    advlink_styles : "",
    external_link_list_url : "/tinymce/tiny_mce_links.js",

    
// FileBrowser
    file_browser_callback : "CustomFileBrowser",
    relative_urls : false,
    
    
// template
	template_cdate_classes : "cdate creationdate",
	template_mdate_classes : "mdate modifieddate",
	template_selected_content_classes : "selcontent",
	template_cdate_format : "%m/%d/%Y : %H:%M:%S",
	template_mdate_format : "%m/%d/%Y : %H:%M:%S",
	template_replace_values : {},
	template_templates : [
    
    ]
});
{% endcomment %}
