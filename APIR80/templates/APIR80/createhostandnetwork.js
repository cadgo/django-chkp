<script>
$(document).ready(function(){
    var wrapper = $("#LastElement");
    $("#NatHideID").click(function(e){
        console.log("Hola2");
         if ( $('#StaticNadEntry').length ){
            console.log("Existe elemento");
            $("#StaticNadEntry").remove();
            }
        var createhead = $(document.createElement('div'));
        createhead.attr("id", "NatHideEntry");
        createhead.html('{% spaceless %}{{ dummyhide }}{% endspaceless %}');
        $("#LastElement").append(createhead);
    });
    $("#StaticNatID").click(function(e){
         console.log("Hola Static Nat");
         if ( $('#NatHideEntry').length ){
            console.log("Existe elemento");
            $("#NatHideEntry").remove();
            }
        var createheadA = $(document.createElement('div'));
        createheadA.attr("id", "StaticNadEntry");
        createheadA.html('{% spaceless %}{{ dummyStatic }}{% endspaceless %}');
        $("#LastElement").append(createheadA);
    });
    $("#NoNat").click(function(f){
        console.log("superhola");
        if ( $('#NatHideEntry').length ){
            console.log("Existe elemento");
            $("#NatHideEntry").remove();
        }
        if ( $('#StaticNadEntry').length ){
            $("#StaticNadEntry").remove();
        }
    });
});
</script>
