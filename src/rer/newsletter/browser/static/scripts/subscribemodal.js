requirejs(["jquery"], function($){
  $(document).ready(function() {
    context = $('.plone-modal-body div #content-core').data('abs') + '/@@unsubscribe';

    portalMessage = $('.portalMessage.error');

    $('div.plone-modal-body').find( portalMessage ).each(function (){
      var email = $('#form-widgets-email').val();
      var href = $('.redirect').attr('href')
      $('.redirect').attr('href', href + '?email=' + email)
      $('.redirect').show();
    });
    $('div.plone-modal-body').find( '.portalMessage' ).each(function (){
      $('.content_container').hide()
      $('.pattern-modal-buttons').hide()
    });
  });
});
