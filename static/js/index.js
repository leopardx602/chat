var startID = 0
var endID = 0
var myID = ''
var roomID = ''
var nowFriendID = ''

var messageID = {} // {'chen01':{'startID':1, 'endID':10, 'text':[]}, 'chen02':{'startID':5, 'endID':8, 'text':[]}}

var tickers = []

var socket = io();

$(document).ready(function () {
  socket.on('connect', function () {
    socket.emit('get_friendID_list');
  });

  socket.on('userID', function (data) {
    myID = data
    console.log('myID', myID)
  });

  socket.on('show_friendID_list', function (data) {
    text = ''
    Object.keys(data).forEach(key => {
      text += `<div onclick=loadRoom('${data[key]}')>${data[key]}</div>`
      messageID[data[key]] = {}
    });
    console.log(messageID)
    $('#friends_body').html(text)
  })


  socket.on('show_room_message', function (data) {
    console.log('show_room_message')
    var friendID = nowFriendID
    messageID[friendID] = {'startID':0, 'endID':0, 'text':[]}

    var text = ''
    Object.keys(data).forEach(key => {
      //console.log(key, data[key]);
      messageID[friendID]['text'].push(data[key])
      //messageID[friendID]['text'].unshift(data[key]['message'])
      if (data[key]['userID'] == myID) {
        text += "<div class='local_box'><div class='local_text'>"
        text += `${data[key]['message']}</div></div>`
      } else {
        text += `<div class='remote_box'><div class='remote_text'>`
        text += `${data[key]['message']}</div></div>`
      }
    });
    
    // if data[0]['id'] < messageID[friendID]['startID']
    messageID[friendID]['startID'] = data[0]['id']
    messageID[friendID]['endID'] = data[data.length - 1]['id']
    
    $("#content").html(text)
    $("#content").scrollTop($("#content")[0].scrollHeight);
  })

  socket.on('show_old_message', function (data) {
    if (data) {
      preHeight = $("#content")[0].scrollHeight
      preTop = $("#content")[0].scrollTop

      var friendID = nowFriendID
      //data = data.reverse()
      console.log('history', data)
      var tmp = []
      let text = ''
      Object.keys(data).forEach(key => {
        tmp.push(data[key])

        if (data[key]['userID'] == myID) {
          text += "<div class='local_box'><div class='local_text'>"
          text += `${data[key]['message']}</div></div>`
        } else {
          text += `<div class='remote_box'><div class='remote_text'>`
          text += `${data[key]['message']}</div></div>`
        }

        if (data[key]['id'] < messageID[friendID]['startID'])
          messageID[friendID]['startID'] = data[key]['id']
      });

      messageID[friendID]['text'] = tmp.concat(messageID[friendID]['text']);

      $('#content').prepend(text)
      startID = data[0]['id']

      nowHeight = $("#content")[0].scrollHeight
      $("#content").scrollTop(nowHeight - preHeight + preTop);
      console.log('height1:', preHeight)
      console.log('height2:', nowHeight)
    }
  })

  socket.on('show_new_message', function (data) {
    console.log('show_new_message')
    var friendID = nowFriendID
    messageID[friendID]['text'].push(data)
    //!@img@!tiger01!@/img<@!

    var msg = data['message']
    var count = (msg.split("!=img=!")).length - 1

    for (i = 0; i < count; i++) {
      start = msg.search("!=img=!")
      end = msg.search("!=/img=!")
      tmp = msg.slice(start, end + 8);
      console.log('tmp', tmp)
      var img = msg.slice(start+7, end-2)
      var id = parseInt(msg.slice(end-2, end), 10)
      msg = msg.replace(tmp, `<img class='gif' src='../static/img/${img}/${img}${id}.gif'>`);

      // `<img class='gif' src='../static/img/${type}/${id}.gif'>`
    }

    var text = ''
    if (data['userID'] == myID){
      text = "<div class='local_box'><div class='local_text'>"
      text += `${msg}</div></div>`
    }
    else{
      text += `<div class='remote_box'><div class='remote_text'>`
      text += `${msg}</div></div>`
    }
    console.log('text', text)


    $("#content").append(text)
    $("#content").scrollTop($("#content")[0].scrollHeight);

    /*
    count = (msg.split("<img class=")).length - 1
      for (i = 0; i < count; i++) {
        start = msg.search("<img class=")
        end = msg.search('.gif">')
        tmp = msg.slice(start, end + 6);
        msg = msg.replace(tmp, "<<tiger01>>");
      }
      socket.emit('send_new_message', msg);*/

    //data = `<img class='gif' src='../static/img/tiger/${id}.gif'>`
    //$("#inputText").append(data);
  })

});


function loadRoom(friendID) {
  nowFriendID = friendID
  $("#chatHead").html(friendID)

  if (Object.keys(messageID[friendID]).length == 0){
    socket.emit('get_room_message', friendID);
  }
  else{
    var data = messageID[friendID]['text']
    var text = ''
    Object.keys(data).forEach(key => {
      if (data[key]['userID'] == myID) {
        text += "<div class='local_box'><div class='local_text'>"
        text += `${data[key]['message']}</div></div>`
      } else {
        text += `<div class='remote_box'><div class='remote_text'>`
        text += `${data[key]['message']}</div></div>`
      }
    });
    $("#content").html(text)
    $("#content").scrollTop($("#content")[0].scrollHeight);
  } 
}


function sendLeft() {
  msg = document.getElementById("inputText").innerHTML
  if (msg) {
    //console.log(msg)
    data = `<div class="remote_box ">`
    data += `<div class="head_sticker ">`
    data += `<div class="pic ">`
    data += `<img src="https://picsum.photos/100/100?random=16 "/>`
    data += `</div>`
    data += `</div>`
    data += "<div class='remote_text'>" + msg + " </div>"
    data += `</div>`

    $("#content").append(data);
    $("#content").scrollTop($("#content")[0].scrollHeight);
  }
}

$(document).ready(() => {
  $("#send").click(() => {
    msg = document.getElementById("inputText").innerHTML
    if (msg) {
      //console.log(msg)
      
      console.log(msg.length)
      /*
      today = new Date();
      data = `<div class="local_box">`
      data += "<div class='local_text'>" + msg + "</div>"
      data += `</div>`

      $("#content").append(data);
      $("#content").scrollTop($("#content")[0].scrollHeight);*/

      count = (msg.split("<img class=")).length - 1
      for (i = 0; i < count; i++) {
        start = msg.search("<img class=")
        end = msg.search('.gif">')
        tmp = msg.slice(start, end + 6);
        var imgID = '' // ttmp
        msg = msg.replace(tmp, "!=img=!tiger01!=/img=!");
      }
      socket.emit('send_new_message', msg);

      /*
      //console.log(msg)
      nowTime = [today.getFullYear(), today.getMonth(), today.getDate(), today.getHours(), today.getMinutes()]
      js = JSON.stringify({
        'id': 'chen',
        'time': nowTime,
        'message': msg
      })

      $.post("/inputText", js, function (data, status) {
        //console.log(data, status)
      });*/
    }

    var today = new Date();
    today.getFullYear()
    today.getMonth()
    today.getDate()
    today.getHours()
    today.getMinutes()
    today.getSeconds()
    today.getMilliseconds()
  })
})

function oldMsg() {
  console.log('oldMsg', nowFriendID)
  var friendID = nowFriendID
  //messageID[friendID]['startID']
  if (messageID[friendID]['startID'] <= 1) return

  socket.emit('get_old_message', {'friendID':friendID, 'startID': messageID[friendID]['startID']});
}


$(document).ready(() => {
  $('#sticker').on('click', () => {
    if ($('#stickers').html().length != 0) {
      $('#stickers').html('')
      return
    }
    let text = ''
    text += '<div id="stickers_head">'
    text += '<div class="left">'
    text += '<div onclick=sticker_change("classic")>經典</div>'
    text += '<div onclick=sticker_change("tiger")>小虎</div>'
    text += '<div onclick=sticker_change("egg")>雞蛋</div>'
    text += '<div onclick=sticker_change("fox")>狐狸</div>'
    text += '</div>'
    text += '<div class="right">'
    text += '<div id="sticker_close">關閉</div>'
    text += '</div>'
    text += '</div>'

    text += '<div id="stickers_body">'

    for (i = 1; i <= 50; i++) {
      text += `<img class='gifIndex' id='tiger${i}' src='../static/img/tiger/tiger${i}.png'>`
      //console.log(`A${i}.gif`)
    }
    text += '</div>'
    //console.log(document.getElementById('sticker').offsetLeft)
    //console.log(document.getElementById('sticker').offsetTop)
    $('#stickers').html(text)

    $('.gifIndex').each(function () {
      $(this).hover(function () {
        path = $(this).attr('src').replace('.png', '.gif')
        $(this).attr('src', path);
      }, function () {
        path = $(this).attr('src').replace('.gif', '.png')
        $(this).attr('src', path);
      })

      $(this).on('click', () => {
        id = $(this).attr('id')
        data = document.getElementById("inputText").innerHTML
        count = (data.split("<img class=")).length - 1
        if (count < 3) {
          data = `<img class='gif' src='../static/img/tiger/${id}.gif'>`
          $("#inputText").append(data);
        }
      });
    })

    $('#sticker_close').on('click', () => {
      $('#stickers').html('')
    });
  });
})


function sticker_change(type) {
  console.log(type)
  text = ''
  for (i = 1; i <= 50; i++) {
    text += `<img class='gifIndex' id='${type}${i}' src='../static/img/${type}/${type}${i}.png'>`
    //console.log(`A${i}.gif`)
  }
  $('#stickers_body').html(text)

  $('.gifIndex').each(function () {
    $(this).hover(function () {
      path = $(this).attr('src').replace('.png', '.gif')
      $(this).attr('src', path);
    }, function () {
      path = $(this).attr('src').replace('.gif', '.png')
      $(this).attr('src', path);
    })

    $(this).on('click', () => {
      id = $(this).attr('id')
      data = document.getElementById("inputText").innerHTML
      count = (data.split("<img class=")).length - 1
      if (count < 3) {
        data = `<img class='gif' src='../static/img/${type}/${id}.gif'>`
        $("#inputText").append(data);
      }
    });
  })
}


/*
$(document).ready(() => {
  $.get("/friendList", function(data) {
    console.log(data)
    text = ''
    Object.keys(data).forEach(key => {
      text += `<div onclick=loadRoom('${data[key]}')>${data[key]}</div>`
    });

    $('#friends_body').html(text)
  })
})*/


function updateMsg() {
  setInterval(() => {
    if (!roomID) return
    js = JSON.stringify({ 'roomID': roomID, 'endID': endID })
    $.post("/loadNewMsg", js, function (data, status) {
      if (data == '') return
      text = ''
      //console.log(data, status)
      Object.keys(data).forEach(key => {
        console.log(key, data[key]);
        if (data[key]['userID'] == myID) {
          text += "<div class='local_box'><div class='local_text'>"
          text += `${data[key]['message']}</div></div>`
        } else {
          text += `<div class='remote_box'><div class='remote_text'>`
          text += `${data[key]['message']}</div></div>`
        }
      });
      //console.log(endID)
      $("#content").append(text)
      $("#content").scrollTop($("#content")[0].scrollHeight);
    });
  }, 1000);
}

$(document).ready(() => {
  $("#addFriend").click(() => {
    text = `<div id="addFriendForm">`
    text += `<div id="addFriendForm_head">`
    text += `<div id="addFriendForm_title">好友邀請</div>`
    text += `<div id="addFriendForm_close" class="btn"><i class="fas fa-times"></i></div>`
    text += `</div>`
    text += `<div>`
    text += `<input type="text" placeholder="好友ID" maxlength="20">`
    text += `</div>`
    text += `<div>`
    text += `<button>發出邀請</button>`
    text += `</div>`
    text += `</div>`
    $("#centerDiv").html(text)
    $("#addFriendForm_close").click(() => {
      $("#centerDiv").html("")
    })
  })

})

