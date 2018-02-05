requirejs(["jquery", "mockup-patterns-modal"], function($, Modal){
  // aspetto che le tile all'interno della pagina siano caricate
  if( $('.pat-tiles-management').length > 0 ){
    $('.pat-tiles-management').on('rtTilesLoaded', function(e) {
      $('#channel-subscribe a').each(function(i, el) {
          modal = new Modal($(el), {
            backdropOptions: {
              closeOnEsc: false,
              closeOnClick: false
            },
            content: '#content',
            loadLinksWithinModal: true,
          });
      });
    });
  }else {
    $('#channel-subscribe a').each(function(i, el) {
        modal = new Modal($(el), {
          backdropOptions: {
            closeOnEsc: false,
            closeOnClick: false
          },
          content: '#content',
          loadLinksWithinModal: true,
        });
    });
  }
});
