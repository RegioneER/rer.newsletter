require.config({
    "paths": {
      "datatables": PORTAL_URL + "/++plone++rer.newsletter/scripts/datatables",
    }
});
requirejs(["jquery", "mockup-patterns-modal", "datatables"], function($, Modal, datatables){

  var table = null;

  $('#users-import > button').on('click', function(){
    $('#users-import > a').click();
  });

  $('#add-user > button').on('click', function(){
    $('#add-user > a').click();
  });

  $('#users-export > button').on('click', function(){
    $.ajax({
      url: "exportUsersListAsFile"
    })
    .done(function(data){

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

  $('#delete-user > button').on('click', function(){
    $.ajax({
      url: "deleteUserFromNewsletter",
      type: "post",
      data: {
        email: table.row('.selected').data().email
      }
    })
    .done(function(data){
      if (JSON.parse(data).ok){
        table.row('.selected').remove().draw( false );
      }
      else{
        alert("problem with user's delete");
      }
    });
  });

  $(document).ready(function() {
    // inizializzazione datatables
    table = $('#users-table').DataTable({
      "ajax": {
            "url": "exportUsersListAsJson",
            "dataSrc": ""
        },
      "columns": [
            { "data": "email" },
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
