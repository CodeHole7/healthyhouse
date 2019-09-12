(function () {

    // Polyfill from https://developer.mozilla.org/en/docs/Web/API/Element/matches
    if (!Element.prototype.matches) {
        Element.prototype.matches =
            Element.prototype.matchesSelector ||
            Element.prototype.mozMatchesSelector ||
            Element.prototype.msMatchesSelector ||
            Element.prototype.oMatchesSelector ||
            Element.prototype.webkitMatchesSelector ||
            function (s) {
                var matches = (this.document || this.ownerDocument).querySelectorAll(s),
                    i = matches.length;
                while (--i >= 0 && matches.item(i) !== this) {
                }
                return i > -1;
            };
    }

    document.addEventListener('DOMContentLoaded', function () {
        initialiseCKEditor();
        initialiseCKEditorInInlinedForms();
    });

    function merge(obj1, obj2) {
        for (var key in obj2) {
            if(!obj2.hasOwnProperty(key)) continue;
            obj1[key] = obj2[key]
        }
        return obj1;
    }

    function initialiseCKEditor() {
        var r = /^<script[\s\S]*?>[\s\S]*?<\/script>/gi;
        var configFromAttr,
            additionalConfig =  {
                toolbar: 'standard',
                width: '100%',
                basicEntities: false,
                disallowedContent: 'script; *[on*]',
                on: {
                    paste: function(evt) {
                        var editor = evt.editor,
                            data;
                        try {
                            data = evt.data.dataTransfer._.data.Text;
                            if(r.test(data)) {
                                editor.setData( '<p>scripts are not allowed</p>' );
                            }
                        } catch (err) {
                            console.warn(err)
                        }
                    },
                }

            };
        var textareas = Array.prototype.slice.call(document.querySelectorAll('textarea[data-type=ckeditortype]'));
        for (var i = 0; i < textareas.length; ++i) {
            var t = textareas[i];
            if (t.getAttribute('data-processed') == '0' && t.id.indexOf('__prefix__') == -1) {
                t.setAttribute('data-processed', '1');
                var ext = JSON.parse(t.getAttribute('data-external-plugin-resources'));
                for (var j = 0; j < ext.length; ++j) {
                    CKEDITOR.plugins.addExternal(ext[j][0], ext[j][1], ext[j][2]);
                }
                CKEDITOR.replace(t.id, JSON.parse(t.getAttribute('data-config')));
                // configFromAttr = JSON.parse(t.getAttribute('data-config'))
                // CKEDITOR.replace(
                //     t.id,
                //     merge(configFromAttr, additionalConfig)
                // );

            }
        }
    }

    function initialiseCKEditorInInlinedForms() {
        document.body.addEventListener('click', function (e) {
            if (e.target && (
                    e.target.matches('.add-row a') ||
                    e.target.matches('.grp-add-handler')
                )) {
                initialiseCKEditor();
            }
        });
    }

}());
