var myID = ''
var myNickName = ''
var nowFriendID = ''
var invitationList = []
var friendList = []  // [{'friendID':'chen01', 'nickName':'Chen'}, {...}]
var friendInfo = {}  // {'chen01':{'nickName':'Chen'}}

var messageID = {} // {'chen01':{'startID':1, 'endID':10, 'text':[]}, 'chen02':{'startID':5, 'endID':8, 'text':[]}}

var socket = io();

$(document).ready(function () {
  socket.on('connect', function () {
    console.log('connect')
    // socket.emit('get_friendID_list');
  });

  socket.on('userInfo', function (data) { // "chen01"
    myID = data['userID']
    myNickName = data['nickName']
    console.log('myID', myID)
  });

  socket.on('show_friendID_list', function (data) { // [{'friendID':'room1', 'nickName':'Chen'}, {...}]
    if (!data) return
    console.log('show_friendID_list', data)
    friendList = data
    Object.keys(data).forEach(key => {
      messageID[data[key]['friendID']] = {}
      friendInfo[data[key]['friendID']] = {'nickName':data[key]['nickName']}
    });
    console.log(messageID)
    console.log('friendInfo', friendInfo)
    show_friendList()
  })

  socket.on('show_invitation', function (data) { // ["chen02", "chen03"]
    invitationList = data
    console.log('invitationList', invitationList)
  })


  socket.on('show_room_message', function (data) { // [{"userID":"chen01", "message":"HI"}, {"userID":"chen02", "message":"Hello"}]
    console.log('show_room_message', data)
    var friendID = nowFriendID
    messageID[friendID] = { 'startID': 0, 'endID': 0, 'text': [] }
    if (!data) return
    var text = ''
    Object.keys(data).forEach(key => {
      //console.log(key, data[key]);
      messageID[friendID]['text'].push(data[key])
      var msg = text_to_sticker(data[key]['message'])

      //messageID[friendID]['text'].unshift(data[key]['message'])
      if (data[key]['userID'] == myID) {
        text += "<div class='local_box'><div class='local_cell message_cell'>"
        text += `${msg}</div></div>`
      } else {
        text += `<div class='remote_box'><div class='remote_cell message_cell'>`
        text += `${msg}</div></div>`
      }
    });

    // if data[0]['id'] < messageID[friendID]['startID']
    messageID[friendID]['startID'] = data[0]['id']
    messageID[friendID]['endID'] = data[data.length - 1]['id']

    $("#content").html(text)
    $("#content").scrollTop($("#content")[0].scrollHeight);
  })

  socket.on('show_old_message', function (data) { // [{"userID":"chen01", "message":"HI"}, {"userID":"chen02", "message":"Hello"}]
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
        var msg = text_to_sticker(data[key]['message'])
        if (data[key]['userID'] == myID) {
          text += "<div class='local_box'><div class='local_cell message_cell'>"
          text += `${msg}</div></div>`
        } else {
          text += `<div class='remote_box'><div class='remote_cell message_cell'>`
          text += `${msg}</div></div>`
        }
        if (data[key]['id'] < messageID[friendID]['startID'])
          messageID[friendID]['startID'] = data[key]['id']
      });

      messageID[friendID]['text'] = tmp.concat(messageID[friendID]['text']);

      $('#content').prepend(text)

      nowHeight = $("#content")[0].scrollHeight
      $("#content").scrollTop(nowHeight - preHeight + preTop);
      console.log('height1:', preHeight)
      console.log('height2:', nowHeight)
    }
  })

  socket.on('show_new_message', function (data) { // {"sendID":"chen01", "recvID":"chen02", "message":"HI"}
    console.log('show_new_message')
    if (nowFriendID == "") return

    var friendID = (myID == data['sendID']) ? data['recvID'] : data['sendID']
    messageID[friendID]['text'].push({ "userID": data['sendID'], "message": data['message'] })

    if (friendID == nowFriendID) {
      var msg = text_to_sticker(data['message'])
      var text = ''
      if (data['sendID'] == myID) {
        text = "<div class='local_box'><div class='local_cell message_cell'>"
        text += `${msg}</div></div>`
      } else {
        text += `<div class='remote_box'><div class='remote_cell message_cell'>`
        text += `${msg}</div></div>`
      }
      console.log('text', text)
      $("#content").append(text)
      $("#content").scrollTop($("#content")[0].scrollHeight);
    }
  })

  socket.on('client_event', function (data) { // ["chen02", "chen03"]
    console.log('client_event', data)
    if (data['event'] == 'invite_message') {
      $("#invite_message").html(data['data'])
    }
  })

  //invite_message
});

function text_to_sticker(msg) { // "Hello world !@img@!tiger01!@/img<@!"
  //!@img@!tiger01!@/img<@!
  var count = (msg.split("!=img=!")).length - 1
  for (i = 0; i < count; i++) {
    var start = msg.search("!=img=!")
    var end = msg.search("!=/img=!")
    var tmp = msg.slice(start, end + 8);
    var img = msg.slice(start + 7, end - 2)
    var imgID = msg.slice(start + 7, end)
    msg = msg.replace(tmp, `<img class='gif' src='../static/img/${img}/${imgID}.gif'>`);
  }
  return msg
}

function loadRoom(friendID) {
  nowFriendID = friendID

  var text = `<div id="chat_headshot">${friendID}</div>`
  
  text += `<div class="friend_name">${friendID}</div>`
  $("#chat_headshot").html(friendInfo[friendID]['nickName'][0])
  $("#chat_name").html(friendInfo[friendID]['nickName'])

  if (Object.keys(messageID[friendID]).length == 0) {
    socket.emit('get_room_message', friendID);
  } else {
    var data = messageID[friendID]['text']
    var text = ''
    Object.keys(data).forEach(key => {
      var msg = text_to_sticker(data[key]['message'])
      if (data[key]['userID'] == myID) {
        text += "<div class='local_box'><div class='local_cell message_cell'>"
        text += `${msg}</div></div>`
      } else {
        text += `<div class='remote_box'><div class='remote_cell message_cell'>`
        text += `${msg}</div></div>`
      }
    });
    $("#content").html(text)
    $("#content").scrollTop($("#content")[0].scrollHeight);
  }
}

function sendMsg(){
  if (nowFriendID == '') return;
  msg = document.getElementById("inputText").innerHTML
  $("#inputText").html("")
  if (msg) {
    //console.log(msg)
    //console.log(msg.length)
    var count = (msg.split("<img class=")).length - 1
    for (i = 0; i < count; i++) {
      var start = msg.search("<img class=")
      var end = msg.search('.png">')

      var subtext = msg.slice(msg.search('/img/') + 5, end)
      console.log('subtext', subtext)
      var imgID = subtext.slice(subtext.search('/') + 1)
      console.log('imgID', imgID)

      var tmp = msg.slice(start, end + 6);
      msg = msg.replace(tmp, `!=img=!${imgID}!=/img=!`);
    }
    data = { "friendID": nowFriendID, "message": msg }
    socket.emit('send_new_message', data);
  }

}

$(document).ready(() => {
  $("#btn_send").click(()=>{
    sendMsg()
  })
  $("#inputText").on('keydown', function(e) {  
    if(e.keyCode == 13){
      sendMsg()
      return e.which != 13;
    }
  })
})

function oldMsg() {
  console.log('oldMsg', nowFriendID)
  var friendID = nowFriendID
  //messageID[friendID]['startID']
  if (messageID[friendID]['startID'] <= 1) return
  socket.emit('get_old_message', { 'friendID': friendID, 'startID': messageID[friendID]['startID'] });
}


$(document).ready(() => {
  $('#sticker').on('click', () => {
    if ($('#stickerList').html() != '') {
      $('#stickerList').html('')
      $('#stickerList').css('display', 'none')
      return
    }
    $('#stickerList').css('display', '')
    let text = ''
    text += '<div id="stickerList_head">'
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
    text += '<div id="stickerList_body">'
    text += '</div>'

    $('#stickerList').html(text)
    sticker_change('tiger')

    $('#sticker_close').on('click', () => {
      $('#stickerList').html('')
      $('#stickerList').css('display', 'none')
    });

  });
})


function sticker_change(type) {
  console.log(type)
  text = ''
  for (i = 1; i <= 50; i++) {
    var num = (i < 10) ? `0${i}` : `${i}`;
    text += `<img class='gifIndex' id='${type}${num}' src='../static/img/${type}/${type}${num}.png'>`
    //console.log(`A${i}.gif`)
  }
  $('#stickerList_body').html(text)

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
        data = `<img class='gifText' src='../static/img/${type}/${id}.png'>`
        $("#inputText").append(data);
      }
    });
  })
}

$(document).ready(() => {
  $("#addFriend").click(() => {
    $('#shadow').css('display', '');

    $("#addFriendForm").css("display", "")
    $("#addFriendForm_close").click(() => {
      $("#addFriendForm").css("display", "none")
      $('#shadow').css('display', 'none');
    })

    $('#btn_invite').click(() => {
      var invitedID = $("#invitedID").val()
      if (invitedID.length < 6 || !checkVal(invitedID)) {
        console.log("no this id")
        return
      }
      socket.emit('add_invitation', invitedID);
    })

    var text = ''
    console.log('invitationList', invitationList)
    Object.keys(invitationList).forEach(key => {
      text += `<div>`
      text += `<div>${invitationList[key]['applicantNickName']}(${invitationList[key]['applicantID']})</div>`
      text += `<div>`
      text += `<button class="btn_confirm" value=${invitationList[key]['applicantID']}>接受</button>`
      text += `<button class="btn_cancel" value=${invitationList[key]['applicantID']}>拒絕</button>`
      text += `</div>`
      text += `</div>`
    });
    $("#addFriendForm_body_invitation").html(text)

    $(".btn_confirm").click(function () {
      socket.emit('reply_invitation', { 'applicantID': $(this).val(), 'reply': true });
      $(this).parent().html('已接受')
    })

    $(".btn_cancel").click(function () {
      socket.emit('reply_invitation', { 'applicantID': $(this).val(), 'reply': false });
      $(this).parent().html('已拒絕')
    })
  })
})

function checkVal(str) {
  var regExp = /^[\d|a-zA-Z]+$/;
  if (regExp.test(str))
    return true;
  else
    return false;
}

function show_friendList() {
  data = friendList  // [{'friendID':'room1', 'nickName':'Chen'}, {...}]
  if (!data) return
  var text = ''
  if ($(window).width() > 850) {
    $("#friends").css("width", "360px")
    $("#friends_head").css("justify-content", "space-between")
    $("#friends_title").css("display", "")
    $(".friend_cell").css("justify-content", "")
    Object.keys(data).forEach(key => {
      data[key]['nickName'] = (data[key]['nickName'] == null) ? data[key]['friendID'] : data[key]['nickName']
      text += `<div class="friend_cell" onclick=loadRoom('${data[key]['friendID']}')>`
      text += `<div class="friend_head">${data[key]['nickName'][0]}</div>`
      //text += `<div class="friend_head"><img src='../static/img/tiger/tiger01.png'></div>`
      text += `<div>`
      text += `<div class="friend_name">${data[key]['nickName']}</div>`
      text += `<div class="friend_message"></div>`
      text += `</div>`
      text += `</div>`
    });
  }
  else {
    $("#friends").css("width", "auto")
    $("#friends_head").css("justify-content", "center")
    $("#friends_title").css("display", "none")
    $(".friend_cell").css("justify-content", "center")
    Object.keys(data).forEach(key => {
      data[key]['nickName'] = (data[key]['nickName'] == null) ? data[key]['friendID'] : data[key]['nickName']
      text += `<div class="friend_cell" onclick=loadRoom('${data[key]['friendID']}')>`
      text += `<div class="friend_head">${data[key]['nickName'][0]}</div>`
      //text += `<div class="friend_head"><img src='../static/img/tiger/tiger01.png'></div>`
      text += `</div>`
    });
  }
  $('#friends_body').html(text)
}

$(document).ready(()=>{
  $(window).on("resize", methodToFixLayout);
  var winHeight = $(window).height();
  var winWidth = $(window).width();
  
  function methodToFixLayout(e) {
    console.log(winHeight, winWidth)
    if (winWidth > 850 && $(window).width() < 850) {
      winWidth = $(window).width()
      show_friendList()
    }
    if (winWidth < 850 && $(window).width() > 850) {
      winWidth = $(window).width()
      show_friendList()
    }
  }
})

$(document).ready(()=>{
  $("#photo").click(()=>{
    text = '<div id="notify_cell">'
    text += '<div>此功能未開放</div>'
    text += "<img class='gif' src='../static/img/tiger/tiger02.gif'>"
    text += '</div>'
    document.getElementById('notifyDiv').innerHTML = text
    window.setTimeout((() =>
      document.getElementById('notifyDiv').innerHTML = ''
      //console.log("Hello!") 
    ), 5000);
  })
  $("#file").click(()=>{
    text = '<div id="notify_cell">'
    text += '<div>此功能未開放</div>'
    text += "<img class='gif' src='../static/img/tiger/tiger02.gif'>"
    text += '</div>'
    document.getElementById('notifyDiv').innerHTML = text
    window.setTimeout((() =>
      document.getElementById('notifyDiv').innerHTML = ''
      //console.log("Hello!") 
    ), 5000);
  })
})

