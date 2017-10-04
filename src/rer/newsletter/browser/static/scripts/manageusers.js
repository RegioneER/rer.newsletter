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

  function renderTables(d){
    var t = $('#users-table').DataTable({
      "ajax": d,
    });
  }

  $(document).ready(function() {
    // chiamata ajax per riempire la tabella
    $.ajax({
      url: "exportUsersListAsJson"
    })
    .done(function(data){
      renderTables(data);
    });
  });
});
