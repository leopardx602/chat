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

  // sign up
  $("#signUp").click(() => { 
    $("#signup_form").css('display', '')
  });
  $("#signup_close").click(() => { 
    $("#signup_form").css('display', 'none')
  });

  $("#sign_up").click(() => { 
    var userID = $("#signup_ID").val()
    var password = $("#signup_password").val()
    var nickName = $("#signup_name").val()
  
    // check input text
    if (userID.length < 6){
      $("#signup_message").html('ID must be at least 6 characters')
      return
    }
    if (password.length < 8){
      $("#signup_message").html('password must be at least 8 characters')
      return
    }
    if (nickName.length < 1){
      $("#signup_message").html('name must be at least 1 characters')
      return
    }
    if (!checkVal(userID) || !checkVal(password) || !checkVal(nickName)){
      $("#signup_message").html('only a-z A-Z 0-9')
      console.log('only a-z A-Z 0-9')
      return
    }
  
    js = JSON.stringify({
      'userID': userID,
      'password': password,
      'nickName':nickName
    })
    $.post("/signup", js, function(data, status) {
      console.log(data, status)
      if (data == 'repeat'){
        $("#signup_message").html('ID is repeated!')
      }
      else if (data == 'ok'){
        $("#signup_message").css('color', 'green')
        $("#signup_message").html('Success!')
      }
    });
  });
});

function checkVal(str) {
  var regExp = /^[\d|a-zA-Z]+$/;
  if (regExp.test(str))
      return true;
  else
      return false;
}