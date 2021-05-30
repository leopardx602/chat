$(document).ready(() => {
  $("#forget").click(() => {
    text = '<div id="notify_cell">'
    text += '<div>自己想</div>'
    text += "<img class='gif' src='../static/img/tiger/tiger50.gif'>"
    text += '</div>'
    document.getElementById('notifyDiv').innerHTML = text
    window.setTimeout((() =>
      document.getElementById('notifyDiv').innerHTML = ''
      //console.log("Hello!") 
    ), 5000);
  });
});

$(document).ready(() => {
  $("#signUp").click(() => {
    text = '<div id="notify_cell">'
    text += '<div>求我呀</div>'
    text += "<img class='gif' src='../static/img/egg/egg40.gif'>"
    text += '</div>'
    document.getElementById('notifyDiv').innerHTML = text
    window.setTimeout((() =>
      document.getElementById('notifyDiv').innerHTML = ''
      //console.log("Hello!") 
    ), 5000);
  });
});