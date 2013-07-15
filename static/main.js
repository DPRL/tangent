MathJax.Hub.Config({
  tex2jax: {inlineMath: [['$','$'], ['\\(','\\)']]}
});

function submitQuery() {
    var query = document.getElementById('query').value;
    window.location = './?query=' + encodeURIComponent(query);
    console.log(query);
}

$(function() {
    $('#query').keypress(function (e) {
      if (e.which == 13) {
        submitQuery();
      }
    });

    $('.result').click(function(e) {
        $(this).toggleClass('selected');
    });
    $('.result a').click(function(e) {
        e.stopPropagation();
    });
});
