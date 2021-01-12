// bar select animation: FadeIn FadeOut
var $active = $('#item1');
$('.items').not($active).hide();

$("#bar button").click(function(event){
  event.preventDefault();
  var $item = $($(this).attr('href'));
  $active.not($item).fadeOut(500).promise().done(function(){
    $item.fadeIn(500);
    $active = $item;
  });
});

// event click: text
// $("#item1 button").click(function(event){
//   var value = document.getElementById("text_input").value;
//   document.getElementById("text_output").innerHTML = value;
// });

// event click: ptt
// $("#item2 button").click(function(event){
//   var value = document.getElementById("ptt_input").value; 
//   document.getElementById("ptt_show").value = value;
//   document.getElementById("ptt_output").innerHTML = value;
// });