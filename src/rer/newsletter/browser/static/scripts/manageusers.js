require.config({
    "paths": {
      "datatables": PORTAL_URL + "/++plone++rer.newsletter/scripts/datatables",
    }
});
requirejs(["jquery", "mockup-patterns-modal", "datatables"], function($, Modal, datatables){

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
      debugger;
    });
  });

  function populateTables(data){
    $('#users-table').DataTable({
      "ajax": {
            "url": "exportUsersListAsJson",
            "dataSrc": ""
        },
      "columns": [
            { "data": "Emails" },
        ]
    });
  }

  $(document).ready(function() {
    // // chiamata ajax per riempire la tabella
    // $.ajax({
    //   url: "exportUsersListAsJson"
    // })
    // .done(function(data){
    //   populateTables(data);
    // });
    $('#users-table').DataTable({
      "ajax": {
            "url": "exportUsersListAsJson",
            "dataSrc": ""
        },
      "columns": [
            { "data": "Emails" },
        ]
    });
  });
});
