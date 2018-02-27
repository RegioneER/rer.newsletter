require.config({
    "paths": {
      "datatables": PORTAL_URL + "/++plone++rer.newsletter/scripts/datatables",
    }
});
requirejs(["jquery", "mockup-patterns-modal", "datatables"], function($, Modal, datatables){

  var table = null;
  var table_line_numbers = 0;

  function render_error(message){
    $('.portalMessage').removeClass('info')
                       .addClass('error')
                       .css('display', '')
                       .html('<strong>Error</strong> ' + message);
  }

  function render_info(message){
    $('.portalMessage').removeClass('error')
                       .addClass('info')
                       .css('display', '')
                       .html('<strong>Info</strong> ' + message);
  }

  function update_users(json){
    debugger;
    message = null;
    num_utenti = json.length - table_line_numbers;
    if( num_utenti > 0 ){
      if( num_utenti == 1 ){
        message = 'Aggiunto un utente';
      }
      else{
        message = 'Aggiunti '+ num_utenti +' utenti';
      }
      render_info(message)
      table_line_numbers = json.length;
    }
    else if( num_utenti < 0 ){
      if( Math.abs(num_utenti) == 1 ){
        render_info('Rimosso un utente.')
      }
      else{
        render_info('Rimossi '+ Math.abs(num_utenti) +' utenti.')
      }
    }
    table_line_numbers = json.length;
  }

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
        render_error('Prima va selezionato un utente.')
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
            render_info('Utente eliminato con successo.')
            table_line_numbers -= 1;
          }
          else{
            render_error('Problemi con la cancellazione dell\'utente.')
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
          table.ajax.reload(function( json ){
            update_users(json)
          });
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
            "dataSrc": "",
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
