require.config({
    "paths": {
      "datatables": PORTAL_URL + "/++plone++rer.newsletter/scripts/datatables",
    }
});
requirejs(["jquery", "mockup-patterns-modal", "datatables"], function($, Modal, datatables){

  $('#users-import > button').on('click', function(){
    $('#users-import > a').click();
  });

  $(document).ready(function() {
  });
});
