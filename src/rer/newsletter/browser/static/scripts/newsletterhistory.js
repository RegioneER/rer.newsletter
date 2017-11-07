require.config({
    "paths": {
      "datatables": PORTAL_URL + "/++plone++rer.newsletter/scripts/datatables",
    }
});
requirejs(["jquery", "datatables"], function($, datatables){
  $(document).ready(function() {
    // inizializzazione datatables
    table = $('#message-table').DataTable({
      "ajax": {
            "url": "getMessageSentDetails",
            "dataSrc": ""
        },
      "columns": [
            { "data": "message"},
            { "data": "active_users"},
            { "data": "send_date"}
        ]
    });
  });
});
