/* Serialization Method:

Structure 

s = [
    {
        'object': {
            'id':...
            }
        'children': [
            {'object': }, 
            {
                'object': {
                    'id':...
                    },
                'children': [ { 'object'... }]
            
            }
        
        ...
        ]
     },
     { 
     
     }
]

*/
var serializedData;
function get_page_object(el) { 
    object = {
        'id': $(el).attr("id"),
        'in_navigation':$(el).find(".navigation_checkbox").val(),
        'is_published':$(el).find(".published_checkbox").val(),
        }
    return object
}

function serialize_li(el) { 
    var new_data;
    var children = $(el).children("ul").children("li");
    var new_data = {'object': get_page_object(el)};
    if (children.length > 0) {
            var child_arr = [];
            $(children).each(function (i) {
            //    console.log(el==this);
                child_arr.push(serialize_li(this));      
            });
            new_data['children'] = child_arr;
        }
    return new_data;
}


function serialize (el) {
    serializedData = [];
    $(el).children().each(function (i) {
        serializedData.push(serialize_li(this));
    });
    return serializedData
}
function prepare_page_tree() {
$(document).ready(function () {
    $('#navigation').jTree({
        showHelper:true,
        hOpacity:0.6,
        //hBg: "#FCC",
        //hColor: "#222",
        pBorder: "1px dashed #CCC",
        pBg: "#EEE",
        pColor: "#222",
        pHeight: "20px",
        snapBack: 80,
        childOff: 40,
        onChange: function (el) { serialize(el); },
        moveHandler: "li div .movespan",

    });
    $("#submit_tree").click(function () {
        data = serialize($('#navigation'));
        //console.log(data);
        data = JSONstring.make(data);
        //console.log(data);
        data = { "json":data }
        //console.log(data);
        $.post("/admin/cms/page/{# TODO: use {% url for this #}", data, function (data, textStatus) {
            if (textStatus == "success") {
                    return true;
                } else {
                    alert("There was an error saving your changes. Please try again");
                }
        });
        return false;
    });
});
}