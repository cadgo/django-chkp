function justprint()
{
    console.log("holaLola");
}
var CreateHost=null;
function CreateHostFrame()
{
    var GetParameters = location.search.substring(1)
    //Tenemos que tomar la URL del navegador y no usar una IP fija
    var UrlTovisti = location.origin + "/r80api/extends/createhost/"
    CreateHost = window.open(UrlTovisti + '?' + GetParameters, "CreateHost", 'location=no,height=570,width=520,scrollbars=yes,status=yes,menubar=no');
    console.log(CreateHost);
}

function CreateNetFrame()
{
    var GetParameters = location.search.substring(1)
    //Tenemos que tomar la URL del navegador y no usar una IP fija
    var UrlTovisti = location.origin + "/r80api/extends/createnetwork/"
    CreateNet = window.open(UrlTovisti + '?' + GetParameters, "CreateNet", 'location=no,height=570,width=520,scrollbars=yes,status=yes,menubar=no');
    console.log(CreateNet);
}

function DeleteHostFrame()
{
    window.opener.location.reload();
    setTimeout(function (){
        window.close();
        },5000);
}

function ReloadPage()
{
    location.reload();
}

/*$(document).ready(function(){
    var wrapper = $("#LastElement");
    $("#NatHideID").click(function(e){
        console.log("Hola2");
         if ( $('#StaticNadEntry').length ){
            console.log("Existe elemento");
            $("#StaticNadEntry").remove();
            }
        var createhead = $(document.createElement('div'));
        createhead.attr("id", "NatHideEntry");
        createhead.html('<p><label for="id_SrcNat">Hide Nat:</label> <select name="SrcNat" id="id_SrcNat"><option value="behind GW">behind GW</option><option value="IP Address">IP Address</option></select></p><p><label for="id_SrcIP">Src NAT IP:</label> <input type="text" name="SrcIP" value="behind GW" required id="id_SrcIP"></p>');
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
        createheadA.html('<p><label for="id_NatIP">Nated IP:</label> <input type="text" name="NatIP" required id="id_NatIP"></p>');
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
});*/
