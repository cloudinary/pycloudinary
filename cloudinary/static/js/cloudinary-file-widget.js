/*global gettext, interpolate */
(function ($) {
  'use strict';
  $(function () {
    $('.cloudinary-fileupload').each(function () {
      var status_element = $('#' + $(this).data('status-element-id'));
      var uploaded_text = $(this).data('uploaded-text');
      $(this).cloudinary_fileupload({
        start: function () {
          status_element.text(gettext('Starting direct upload...'));
        },
        progress: function (e, data) {
          var progress = Math.round((data.loaded * 100.0) / data.total);
          status_element.text(interpolate('Uploading...%s%', [progress]));
        }
      }).on('cloudinaryfail', function (e, data) {
        status_element.text(interpolate('Upload failed. %s: %s', [data.textStatus, data.errorThrown]));
      }).on('cloudinarydone', function (e, data) {
        status_element.text(gettext('Uploaded'));
        status_element.html(interpolate('%s: <a href="%s">%s</a>', [uploaded_text, data.result.url, data.result.public_id]));
      });
    });
  });
})(django.jQuery);
