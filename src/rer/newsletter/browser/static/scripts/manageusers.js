require.config({
    "paths": {
      "datatables": PORTAL_URL + "/++plone++rer.newsletter/scripts/datatables",
    }
});
requirejs(["jquery", "mockup-patterns-modal", "datatables"], function($, Modal, datatables){

  var table = null;

  $(document).ready(function() {

    // triggero l'apertura delle modal
    $('#users-export > span').on('click', function(){
      $.ajax({
        url: "exportUsersListAsFile"
      })
      .done(function(data){
        debugger;
        var blob = new Blob(["\ufeff", data]);
        var url = URL.createObjectURL(blob);

        var downloadLink = document.createElement("a");
        downloadLink.href = url;
        downloadLink.download = "data.csv";

        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
      });
    });

    $('#delete-user > span').on('click', function(){

      if (!(table.row('.selected').data())){
        // render error user deleted
        $('.portalMessage').removeClass('info')
                           .addClass('error')
                           .css('display', '')
                           .html('<strong>Error</strong>Prima va selezionato un utente.');
      }
      else{
        $.ajax({
          url: "deleteUser",
          type: "post",
          data: {
            email: table.row('.selected').data().email
          }
        })
        .done(function(data){
          if (JSON.parse(data).ok){
            table.row('.selected').remove().draw( false );

            // render info user deleted
            $('.portalMessage').removeClass('error')
                               .addClass('info')
                               .css('display', '')
                               .html('<strong>Info</strong>Utente eliminato con successo.');
          }
          else{
            // render error user deleted
            $('.portalMessage').removeClass('info')
                               .addClass('error')
                               .css('display', '')
                               .html('<strong>Error</strong>Problemi con la cancellazione dell\'utente.');
          }
        });
      }
    });

    new Modal($('#button-add-user'), {
      backdropOptions: {
        closeOnEsc: false,
        closeOnClick: false
      },
      actionOptions: {
        onSuccess: function($action, response, options){
          table.ajax.reload();
          $action.$modal.trigger('destroy.plone-modal.patterns');
        }
      },
    });
    new Modal($('#button-import-users'), {
      backdropOptions: {
        closeOnEsc: false,
        closeOnClick: false
      },
      actionOptions: {
        onSuccess: function($action, response, options){
          table.ajax.reload();
          $action.$modal.trigger('destroy.plone-modal.patterns');
        }
      },
    });

    // inizializzazione datatables
    table = $('#users-table').DataTable({
      "language": {
                "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Italian.json"
            },
      "ajax": {
            "url": "exportUsersListAsJson",
            "dataSrc": ""
        },
      "columns": [
            { "data": "email"},
            { "data": "creation_date"},
            { "data": "is_active"}
        ]
    });

    $('#users-table tbody').on( 'click', 'tr', function () {
        if ( $(this).hasClass('selected') ) {
            $(this).removeClass('selected');
        }
        else {
            table.$('tr.selected').removeClass('selected');
            $(this).addClass('selected');
        }
    });

  });
});
