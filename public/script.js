$(document).ready(function () {

    var uid = "";

    $('.cancella').on('click', function () {
        uid = $(this).attr("data-uid");
        var index = uid - 1;
        var name = $(".name:eq("+ index +")").text();
        var phone = $(".phone:eq("+ index +")").text();
        $('#nome-contatto').text(name);
        $('#numero-telefono').text(phone);
    });

    $('#submit-delete').on('click', function () {
        $.post( "process_delete", {uid: uid });
        window.location.href = "/";
    });

    $('#formAdd').on('submit', function (){
        var name = $("#nome").val();
        var phone = $("#telefono").val();
        if(name.length == 0 || phone.length == 0){
            alert("Name or phone missed!")
            return false;
        }
        return true;
    });

});