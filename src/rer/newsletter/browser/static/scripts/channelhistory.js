require.config({
    "paths": {
      "datatables": PORTAL_URL + "/++plone++rer.newsletter/scripts/datatables",
    }
});
requirejs(["jquery", "datatables"], function($, datatables){
  $(document).ready(function() {
    // inizializzazione datatables
    table = $('#message-table').DataTable({
      "language": {
                "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Italian.json"
            },
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
