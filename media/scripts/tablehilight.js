$(document).ready(
    function(){
      $("table.hilightrow tr").mouseover(function(){ $(this).addClass("hilight") });
     $("table.hilightrow tr").mouseout(function(){ $(this).removeClass("hilight") });
    }
);