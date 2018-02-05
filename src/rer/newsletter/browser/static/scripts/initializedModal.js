requirejs(["jquery", "mockup-patterns-modal"], function($, Modal){
  // aspetto che le tile all'interno della pagina siano caricate
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
});
