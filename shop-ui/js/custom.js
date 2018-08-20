function getCookie(name) {
 var cookieValue = null;
 if (document.cookie && document.cookie != '') {
     var cookies = document.cookie.split(';');
     for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
     }
 }
 return cookieValue;
}
var csrftoken = getCookie('csrftoken');

$(document).ready(function(){
  var viewPort = $(window).width();
  var ratioConstant = 0.017371601208459216;
  var anotherConstant = 0.014322916666666666;

  $('.capt-header').css({"font-size":viewPort*ratioConstant});
  $('.capt-p').css({"font-size":viewPort*anotherConstant});


    var alertModal = $('#alertModal');
    $(".item_add").click(function(){
         var product_id = $(this).data('value');
         // Sending a post request to backend containing product id
         $.post('/add-to-cart', {csrfmiddlewaretoken: csrftoken,'product_id': product_id,'quantity':1},function(data){

                   //alert(data)
                   //console.log(alertModal)
                   alertModal.modal('show');
                   $(".alert-message").text(data)
         });
    });

    //adding products to session on a single page
    $(".item_add_single").click(function(){
         var product_id = $(this).data('value');
         var quantity = $(".quantity-value").val();
         //alert(quantity)
         // Sending a post request to backend containing product id
         $.post('/add-to-cart', {csrfmiddlewaretoken: csrftoken,'product_id': product_id,'quantity':quantity},function(data){

               alertModal.modal('show');
               $(".alert-message").text(data)
         });
    });
    // Order Now
    $("#orderNow").click(function(){
         var product_id = $(this).data('value');
         var quantity = $(".quantity-value").val();
         //alert(quantity)
         // Sending a post request to backend containing product id
         $.post('/add-to-cart', {csrfmiddlewaretoken: csrftoken,'product_id': product_id,'quantity':quantity},function(data){
               window.location.assign('/checkout');
         });
    });
    //adding quantity is checkout page
    $(".checkout-add").click(function(e){
      e.preventDefault();
      var parent = $(this).closest('.check')
          quantity = parent.children('.checkout-quantity').val();
         var product_id = $(this).data('id');
         //alert(product_id + "and" + quantity)
         $.post('/editsession', {csrfmiddlewaretoken: csrftoken,'product_id': product_id,'quantity':quantity},function(data){
           if (data == 'saved') {
               window.location.assign('checkout');
           }
         });
    });

    //displaying a form for customer
    $("#fill-form").click(function(){
      $("#customerDetails").show();

    });

});
