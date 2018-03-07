requirejs(["jquery", "mockup-patterns-modal"], function($, Modal){

  function hide_element_modal(){
    $('.content_container').hide()
    $('.pattern-modal-buttons').hide()
  }

  function subscribe_modal(){
    context = $('.plone-modal-body div #content-core .subscription_form').data('abs') + '/@@unsubscribe';
    if ( context ){
      portalMessage = $('.portalMessage.error');

      $('div.plone-modal-body').find( portalMessage ).each(function (){
        // trovare un metodo migliore
        if ($(portalMessage).text().search("Sei già iscritto a questa newsletter, oppure non hai ancora confermato l'iscrizione") > -1){
          hide_element_modal();

          var email = $('#form-widgets-email').val();
          var href = $('.redirect').attr('href')
          $('.redirect').attr('href', href + '?email=' + email)
          $('.redirect').show();
        }
      });
      $('div.plone-modal-body').find( '.portalMessage.info' ).each(function (){
        hide_element_modal();
      });
    }
  }

  function render_modal(el){
    modal = new Modal($(el), {
      backdropOptions: {
        closeOnEsc: true,
        closeOnClick: false
      },
      content: '#content',
      loadLinksWithinModal: true,
      templateOptions: {
        classFooterName: 'plone-modal-footer subscribe_modal',
      }
    });
    modal.on('after-render', subscribe_modal);
    modal.on('shown', function(){
      modal.$modal[0].tabIndex = -1;
      document.getElementById('form-widgets-email').focus();
      $('.plone-modal-close').attr('title', 'chiudi');
    });
  }

  // aspetto che le tile all'interno della pagina siano caricate
  $(document).ready(function(){
    if( $('.pat-tiles-management').length > 0 ){
      $('.pat-tiles-management').on('rtTilesLoaded', function(e) {
        $('#channel-subscribe a').each(function(i, el) {
            render_modal(el)
        });
      });
    }else {
      $('#channel-subscribe a').each(function(i, el) {
        render_modal(el)
      });
    }
  });
});
