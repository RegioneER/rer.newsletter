requirejs(["jquery", "mockup-patterns-modal"], function($, Modal){

  function hide_element_modal(){
    $('#content-core').remove();
    $('.content_container').remove();
    $('.pattern-modal-buttons input').remove();
  }

  function setInput(firstInput, lastInput, closeInput){
    firstInput.focus();

    lastInput.on('keydown', function(e) {
      if (e.which === 9) {
        if (!e.shiftKey) {
          e.preventDefault();
          closeInput.focus();
        }
      }
    });

    firstInput.on('keydown', function(e) {
      if (e.which === 9) {
        if (e.shiftKey) {
          e.preventDefault();
          closeInput.focus();
        }
      }
    });

    $('.button-plone-modal-close').on('click', function() {
      $('.plone-modal-close').click();
    });

    closeInput.on('keydown', function(e) {
      if (e.which === 9) {
        e.preventDefault();

        if (e.shiftKey) {
          lastInput.focus();
        } else {
          firstInput.focus();
        }
      }
    });
  }

  function subscribe_modal(){
    context = $('.plone-modal-body div #content-core .subscription_form').data('abs') + '/@@unsubscribe';
    if ( context ){
      portalMessage = $('.portalMessage.error');

      $('div.plone-modal-body').find( portalMessage ).each(function (){

        if (portalMessage.text().search("Error") > -1){
          portalMessage.html(portalMessage.text().replace("Error", "<b>Attenzione</b>"));
        }

        // trovare un metodo migliore
        if ($(portalMessage).text().search("Sei già iscritto a questa newsletter, oppure non hai ancora confermato l'iscrizione") > -1){
          var email = $('#form-widgets-email').val();
          var href = $('.redirect').attr('href')

          hide_element_modal();

          $('.redirect').attr('href', href + '?email=' + email)
          $('.redirect').show();

          // modifica accessibilità
          setInput($('.redirect'), $('.redirect'), $('.button-plone-modal-close'));
        }
      });
    }
  }

  function init(){
    $('.plone-modal-close').attr('title', 'chiudi');
    $('.pattern-modal-buttons').prepend(
      $('.button-plone-modal-close')
    );

    $('div.plone-modal-body').find( '.portalMessage.info' ).each(function (){
      hide_element_modal();
    });

    // modifica accessibilità
    var inputs = $('.plone-modal-wrapper').find(
      'select, textarea, .redirect, button, input'
    );
    setInput(inputs.first(), inputs.last(), $(inputs.splice(inputs.length - 1, 1)[0]));
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
      init();
    });
    modal.on('afterDraw', function(){
      init();
    });
    modal.on('linkActionSuccess', function(){
      init()
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
